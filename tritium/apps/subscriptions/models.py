from .. import model_base
from django.db import models
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
import json
import requests
import logging
from django.conf import settings
from decimal import Decimal
from tritium.apps.networks.models import MAIN_NETWORK
from tritium.apps.metrics import count_metrics

log = logging.getLogger('subscriptions')
log.setLevel(logging.DEBUG)


class Subscription(model_base.NicknamedBase):
    objects = models.Manager()
    notify_email = models.CharField(max_length=512, null=True, blank=True)
    watched_address = models.CharField(max_length=64)
    user = models.ForeignKey(get_user_model(), on_delete=models.DO_NOTHING)
    notify_url = models.CharField(max_length=2048, null=True, blank=True)
    archived_at = models.DateTimeField(null=True, blank=True)
    watch_token_transfers = models.BooleanField(default=False)
    daily_emails = models.BooleanField(default=False)
    weekly_emails = models.BooleanField(default=False)
    monthly_emails = models.BooleanField(default=False)
    realtime_emails = models.BooleanField(default=True)
    realtime_webhooks = models.BooleanField(default=False)
    include_pricing_data = models.BooleanField(default=False)
    specific_contract_calls = models.BooleanField(default=False)
    abi_methods = models.TextField(null=True, blank=True)
    low_balance_warning = models.BooleanField(default=False)
    network = models.ForeignKey(
        "networks.Network", null=True, on_delete=models.DO_NOTHING)
    STATUS_CHOICES = [('active', 'active'), ('paused', 'paused')]
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default='active')

    def found_transaction(self, tx):
        from tritium.apps.contracts.models import PriceLookup, Contract
        # Too noisy, getting expensive
        #log.info('Found transaction: %s' % tx)

        credits = 0
        charges = []

        if self.status == 'paused':
            log.debug(
                'Subscription is paused, skipping transaction')
            count_metrics('tx.subscription_paused', {
                          'network': self.network.nickname})
            return

        if SubscribedTransaction.objects.filter(tx_hash=tx['hash'], subscription=self):
            log.debug('Already seen this transaction before, skipping')
            count_metrics('tx.duplicate_transaction', {
                          'network': self.network.nickname})
            return

        if not 'datetime' in tx:
            log.error('WHAT THE HELL GUY, NO DATETIME')
            count_metrics('tx.error_missing_datetime', {
                          'network': self.network.nickname})
            return

        
        parameters = None
        if tx['hasData'] and self.specific_contract_calls:
            contract = Contract.LOOKUP(tx['to'])
            w3c = contract.get_web3_contract()
            function = w3c.get_function_by_selector(tx['input'][:10])
            if function.fn_name not in self.abi_methods.split(','):
                log.debug('Not watching this function: %s' % function.fn_name)
                count_metrics('tx.function_not_watched', {
                              'network': self.network.nickname})
                return
            else:
                charges.append('Method: %s' % function.fn_name)
                credits += settings.SPECIFIC_CALLS_CREDIT_COST
                parameters = {
                    'abi': function.abi,
                    'values': w3c.decode_function_input(tx['input'])[1]
                }

        else:
            if self.watch_token_transfers == False:
                if tx['isToken']:
                    log.debug(
                        'Its a token transaction and we arent watching tokens, skip')
                    count_metrics('tx.tokens_not_watched', {
                        'network': self.network.nickname})
                    return
            else:
                if tx['isToken']:
                    credits += settings.TOKEN_TRANSFERS_CREDIT_COST
                    charges.append('Token Transaction')

        if self.include_pricing_data:
            credits += settings.PRICING_DATA_CREDIT_COST
            charges.append('Pricing Data')
            price_info = PriceLookup.get_latest('ETH')
        else:
            price_info = None

        stx = SubscribedTransaction.objects.create(
            subscription=self,
            created_at=tx['datetime'],
            block_hash=tx['blockHash'],
            block_number=tx['blockNumber'],
            from_address=tx['from'],
            gas=tx['gas'],
            gas_price=tx['gasPrice'],
            tx_hash=tx['hash'],
            tx_input=tx['input'],
            nonce=tx['nonce'],
            to_address=tx['to'],
            transaction_index=tx['transactionIndex'],
            value=tx['value'],
            has_data=tx['hasData'],
            is_token=tx['isToken'],
            token_amount=tx.get('tokenAmount', 0),
            token_to=tx.get('tokenTo', ''),
            price_lookup=price_info,
            parameters_json=parameters and json.dumps(parameters) or None
        )

        tx.pop('datetime', '')  # not serializable

        output = {
            'transaction': stx.serialize(),
            'subscription': self.serialize()
        }

        if self.notify_url and self.realtime_webhooks:
            log.debug('Webhook TX Notification to %s' % self.notify_url)
            try:
                r = requests.post(self.notify_url, json=output)
                log.debug('Webhook response: %s' % r.content)
                count_metrics('tx.notify_webhook_success', {
                              'network': self.network.nickname})
                credits += settings.NOTIFICATION_CREDIT_COST
                charges.append('Webhook')
            except Exception as e:
                count_metrics('tx.notify_webhook_error', {
                              'network': self.network.nickname})

        if self.notify_email and self.realtime_emails:
            log.debug('Email TX Notification to %s' % self.notify_email)

            sent = self.send_notification(
                '%s: Transaction Received' % self.nickname,
                json.dumps(output, indent=2)
            )

            credits += settings.NOTIFICATION_CREDIT_COST * sent
            charges.append('Real-time Email')

        if self.low_balance_warning:
            balance = self.network.get_balance(self.watched_address)
            spent = stx.value + stx.gas * stx.gas_price
            if balance <= spent * 10:
                self.send_notification('%s: Low Balance' % self.nickname,
                'The balance of address %s is too low to sustain transactions of size %s; %s remaining'%
                (self.watched_address, spent, balance/10E18)
                )

        reason = ('Transaction [%s]: ' % self.nickname) + ','.join(charges)
        if not self.user.subtract_credit(credits, reason):
            self.status = 'paused'
            self.save()

        

    def send_notification(self, subject, body):
        sent = 0
        for email in self.notify_email.split(','):
            try:
                send_mail(
                    subject, body,
                    'noreply@txgun.io',
                    [email.strip()],
                )
                count_metrics('tx.notify_email_success', {
                            'network': self.network.nickname})
                sent += 1  
            except Exception as e:
                count_metrics('tx.notify_email_error', {
                            'network': self.network.nickname})
        return sent

    def serialize(self):
        from .serializers import SubscriptionSerializer
        return SubscriptionSerializer(self).data

    class Meta:
        ordering = ('-created_at',)


class SubscribedTransaction(model_base.RandomPKBase):
    objects = models.Manager()
    created_at = models.DateTimeField()
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE,
                                     related_name='transactions')
    block_hash = models.TextField()
    block_number = models.PositiveIntegerField()
    from_address = models.CharField(max_length=64)
    gas = models.PositiveIntegerField()
    gas_price = models.DecimalField(max_digits=50, decimal_places=0)
    tx_hash = models.CharField(max_length=128, db_index=True)
    tx_input = models.TextField()
    parameters_json = models.TextField(null=True, blank=True)
    nonce = models.PositiveIntegerField()
    to_address = models.CharField(max_length=64)
    transaction_index = models.PositiveIntegerField()
    value = models.DecimalField(max_digits=50, decimal_places=0)
    has_data = models.BooleanField()
    is_token = models.BooleanField()
    token_amount = models.DecimalField(max_digits=50, decimal_places=0)
    token_to = models.CharField(max_length=64)
    price_lookup = models.ForeignKey('contracts.PriceLookup',
                                     null=True, blank=True, on_delete=models.DO_NOTHING)

    def serialize(self):
        from .serializers import SubscribedTransactionSerializer
        return SubscribedTransactionSerializer(self).data

    @property
    def parameters(self):
        try:
            return json.loads(self.parameters_json)
        except:
            return {}

    def get_pricing_info(self):
        if self.price_lookup:
            return {
                'price': self.get_price(),
                'currency': self.get_currency(),
                'fiat': self.get_fiat(),
                'asset': self.get_asset()
            }

    def get_price(self):
        if self.price_lookup:
            return self.price_lookup.price

    def get_asset(self):
        if self.price_lookup:
            return self.price_lookup.asset

    def get_currency(self):
        if self.price_lookup:
            return self.price_lookup.currency

    def get_fiat(self):
        if self.price_lookup and self.value:
            return self.price_lookup.price * self.value/Decimal(10E18)

    def get_token(self):
        from tritium.apps.contracts.models import ERC20
        if not self.is_token:
            return None
        try:
            return ERC20.objects.get(contract__address=self.to_address)
        except ERC20.DoesNotExist:
            return None

    class Meta:
        ordering = ('-created_at',)
