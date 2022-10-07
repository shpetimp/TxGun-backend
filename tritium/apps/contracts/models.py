from .. import model_base
from django.db import models
import requests
import pytz
from web3 import Web3
from datetime import datetime, timedelta
from requests import Request, Session
from django.conf import settings
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
from django.utils import timezone
import json
from tritium.apps.metrics import count_metrics


class Interface(model_base.NicknamedBase):
    abi = models.TextField(null=True, blank=True)


def get_etherscan_abi(address):
    count_metrics('api.get_etherscan_abi')
    url = settings.ETHSCAN_URL + 'module=contract&action=getabi&address=' + address
    response = requests.get(url)
    return json.loads(response.content)['result']


class Contract(model_base.NicknamedBase):
    network = models.ForeignKey(
        'networks.Network', on_delete=models.DO_NOTHING)
    address = models.CharField(max_length=255)
    abi = models.TextField(null=True, blank=True)
    interfaces = models.ManyToManyField(Interface)

    @classmethod
    def LOOKUP(cls, address, network='mainnet'):
        from tritium.apps.networks.models import DEFAULT
        if isinstance(network, str):
            network = DEFAULT()[network]
        
        find = cls.objects.filter(network=network, address__iexact=address)
        if find.count():
            result = find.first()
        else:
            result = cls.objects.create(address=address, network=network)
            result.get_etherscan_abi()
        try:
            result.address = Web3.toChecksumAddress(address)
            result.save()
        except ValueError as e:
            pass

        return result

    def abi_object(self):
        try:
            return json.loads(json.loads(self.abi))
        except:
            return json.loads(self.abi)

    def get_etherscan_abi(self):
        self.abi = json.dumps(get_etherscan_abi(self.address))
        self.save()

    def get_web3_contract(self):
        if not self.abi:
            self.get_etherscan_abi()
        driver = settings.WEB3_DRIVERS['main']
        return driver.eth.contract(address=self.address, abi=self.abi_object())


class ERC20(model_base.NicknamedBase):
    symbol = models.CharField(max_length=64)
    decimal_places = models.PositiveIntegerField()
    contract = models.ForeignKey(Contract, on_delete=models.DO_NOTHING)

    @classmethod
    def DISCOVERED_TOKEN(cls, network, address):
        contract, _new = Contract.objects.get_or_create(
            network=network, address=address)
        if not _new:
            return None, _new

        contract.interfaces.add(Interface.UNIQUE('evmTransfer'))
        try:
            web3contract = contract.get_web3_contract()
            name = web3contract.functions.name().call()
            decimal_places = web3contract.functions.decimals().call()
            symbol = web3contract.functions.symbol().call()
        except Exception as e:
            token, _new = cls.objects.get_or_create(
                contract=contract,
                defaults={'nickname': 'Error importing token: %s'%e,
                          'symbol': 'ERROR', 'decimal_places': 0}
            )
            raise e

        if not contract.nickname:
            contract.nickname = name
            contract.save()
        try:
            token, _new = cls.objects.get_or_create(
                contract=contract,
                defaults={'nickname': name, 'symbol': symbol,
                          'decimal_places': decimal_places}
            )
        except Exception as e:
            token, _new = cls.objects.get_or_create(
                contract=contract,
                defaults={'nickname': 'Error importing token: %s'%e,
                          'symbol': 'ERROR', 'decimal_places': 0}
            )
            raise e

        return token, _new


class PriceLookup(model_base.RandomPKBase):
    created_at = models.DateTimeField(auto_now_add=True)
    asset = models.CharField(max_length=16)
    currency = models.CharField(max_length=4, default='USD')
    price = models.DecimalField(max_digits=20, decimal_places=10)

    def __str__(self):
        return '%s: 1%s = %s%s' % (
            self.created_at,
            self.asset,
            self.price,
            self.currency
        )

    @classmethod
    def get_latest(cls, asset, currency='USD'):
        try:
            recent = timezone.now()-timedelta(minutes=10)
            return cls.objects.get(asset=asset, created_at__gte=recent)
        except cls.DoesNotExist:
            return cls.objects.create(asset=asset, price=cls.do_lookup(asset, currency))

    @classmethod
    def do_lookup(cls, asset, currency='USD'):
        if asset == 'ETH':
            url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'
            count_metrics('api.coinmarketcap_get_price')
            parameters = {
                'symbol': asset,
                'convert': currency
            }
            headers = {
                'Accepts': 'application/json',
                'X-CMC_PRO_API_KEY': settings.CMC_API_KEY
            }

            session = Session()
            session.headers.update(headers)

            try:
                response = session.get(url, params=parameters)
                data = json.loads(response.text)
                return data['data'][asset]['quote'][currency]['price']
            except (ConnectionError, Timeout, TooManyRedirects) as e:
                print(e)
