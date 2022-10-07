from django.db import models
from .. import model_base
from tritium.conf import eth
from web3 import Web3, HTTPProvider
from datetime import datetime, timedelta
from django.utils import timezone
import random
import pytz
import time
import logging
import sys
from tritium.apps.metrics import count_metrics

scanlog = logging.getLogger('scanner')


class EthDriver(object):
    def __init__(self, endpoint):
        self.web3 = Web3(HTTPProvider(endpoint))

    def current_block(self):
        return self.web3.eth.blockNumber

    def get_block(self, block_number):
        return self.web3.eth.getBlock(block_number, full_transactions=True)

    def get_balance(self, address):
        return self.web3.eth.getBalance(Web3.toChecksumAddress(address))

    def find_transactions(self, block_number, retry=True):
        scanlog.debug('find_transactions: block=%s' % block_number)
        block = self.get_block(block_number)

        # Been some odd errors where block is None...
        # My best guess is that it's the head block
        if not block and retry:
            scanlog.warning(
                'find_transactions: got a null block, retrying in 2 seconds...')
            time.sleep(2)
            return self.find_transactions(block_number, retry=False)

        at = datetime.fromtimestamp(block['timestamp'])
        at = at.replace(tzinfo=pytz.utc).isoformat()

        for rawtx in block.get('transactions', []):
            tx = dict(rawtx)
            tx['datetime'] = at
            tx['hasData'] = 'input' in tx and tx['input'] != '0x'
            tx['isToken'] = False
            if tx['hasData'] and tx['input'].startswith('0xa9059cbb'):
                tx['isToken'] = True
                tx['tokenAmount'] = Web3.toInt(hexstr=tx['input'][-32:])
                START_BYTE = 2 + 8 + (64 - 40)  # 0x a9059cbb [24 0s] [address]
                address = '0x' + tx['input'][START_BYTE:START_BYTE+40]
                try:
                    tx['tokenTo'] = Web3.toChecksumAddress(address)
                except ValueError as e:
                    from tritium.apps.errors.models import ErrorLog
                    ErrorLog.objects.create(
                        nickname="Missing or corrupt input data, examine transaction",
                        traceback='Transaction: %s\n%s' % (tx, e))
                    tx['tokenTo'] = address

            for key in ['hash', 'blockHash']:
                tx[key] = tx[key].hex()

            tx.pop('r', '')
            tx.pop('s', '')
            tx.pop('v', '')

            yield tx


class Software(model_base.NicknamedBase):
    def get_driver(self, network):
        if(self.nickname == 'Ethereum'):
            return EthDriver(network.endpoint)

    @classmethod
    def ETHEREUM(cls):
        return cls.UNIQUE('Ethereum')


class Network(model_base.NicknamedBase):
    software = models.ForeignKey(Software, on_delete=models.DO_NOTHING)
    endpoint = models.TextField()

    @classmethod
    def MAIN(cls):
        return MAIN_NETWORK()

    @classmethod
    def ROPSTEN(cls):
        return ROPSTEN_NETWORK()

    @property
    def driver(self):
        if not hasattr(self, '_driver'):
            setattr(self, '_driver', self.software.get_driver(self))
        return self._driver

    def current_block(self):
        return self.driver.current_block()

    def get_balance(self, address):
        return self.driver.get_balance(address)


class Scanner(model_base.NicknamedBase):
    network = models.ForeignKey(Network, on_delete=models.DO_NOTHING)
    latest_block = models.PositiveIntegerField(default=0)
    locked_thread_time = models.DateTimeField(null=True, blank=True)

    def get_watched_addresses(self):
        # TODO: IF LENGTH OF WATCHED > 2000 MAIL ADMINS
        from tritium.apps.subscriptions.models import Subscription
        watched_addresses = [
            s.watched_address for s in Subscription.objects.all()]
        cleaned = list(map(lambda s: s.lower().strip(), watched_addresses))
        return cleaned

    def in_watch_cache(self, tx):
        # We'll eventually need to move the lookup to
        # a sql query, once it is no longer memory efficient
        # to do here
        def get(key): return (tx.get(key, '') or '').lower()
        to = get('to')
        frm = get('from')
        tkto = get('tokenTo')
        return to in self.watched_cache or frm in self.watched_cache or tkto in self.watched_cache

    def get_available_lock(self):
        now = timezone.now()
        if self.locked_thread_time:
            unlock_time = self.locked_thread_time + timedelta(seconds=150)
            if unlock_time <= now:
                self.release_lock()
            else:
                return False

        self.locked_thread_time = now
        self.save()
        return True

    def release_lock(self):
        scanlog.debug('Releasing scanner lock...')
        self.locked_thread_time = None
        self.save()

    @property
    def watched_cache(self):
        if not hasattr(self, '_watched_addresses'):
            setattr(self, '_watched_addresses',
                    self.get_watched_addresses())
        return self._watched_addresses

    def next_block_to_scan(self):
        current = self.network.driver.current_block()
        if current > self.latest_block:
            return self.latest_block + 1

    def process_next_block(self):
        next_block = self.next_block_to_scan()
        if not next_block:
            return None
        self.process_block(next_block)
        self.latest_block = next_block
        self.save()

    def process_block(self, block_number, save_transactions=False):
        transactions = list(
            self.network.driver.find_transactions(block_number))

        scanlog.info('Processing block: %s @ %s - %s transactions' % (
            self.network, block_number, len(transactions)))

        if save_transactions:
            import json
            fh = open('tests/transactions/block-%s.json' % block_number, 'w+')
            json.dump(transactions, fh, indent=2)

        
        self.process_transactions(transactions)
        
        # At the very end
        count_metrics('scanner.process_block', {'network': self.network.nickname})


    def process_transactions(self, transactions):
        from tritium.apps.subscriptions.models import Subscription
        from tritium.apps.contracts.models import ERC20
        count = 0
        for tx in transactions:
            count += 1
            tx_timer = time.time()
            if self.in_watch_cache(tx):
                scanlog.debug('Found transaction: %s' % tx)
                find_subscribers = (
                    models.Q(watched_address__iexact=tx['to']) |
                    models.Q(watched_address__iexact=tx['from'])
                )
                if(tx['isToken']):
                    find_subscribers = (
                        find_subscribers |
                        models.Q(watched_address__iexact=tx['tokenTo'])
                    )
                subscriptions = Subscription.objects.filter(find_subscribers)
                #count_metrics('scanner.timers.filter_subscriptions', {'network': self.network.nickname}, time.time() - tx_timer, 'Seconds')
                for subscription in subscriptions:
                    subscription_timer = time.time()
                    subscription.found_transaction(tx)
                    #count_metrics('scanner.timers.found_transaction', {'network': self.network.nickname}, time.time() - subscription_timer, 'Seconds')
                if tx.get('isToken'):
                    token_timer = time.time()
                    try:
                        ERC20.DISCOVERED_TOKEN(self.network, tx['to'])
                        #count_metrics('scanner.token_discovered', {'network': self.network.nickname})
                        #count_metrics('scanner.timers.discover_token', {'network': self.network.nickname}, time.time() - token_timer, 'Seconds')
                    except Exception as e:
                        from tritium.apps.errors.models import ErrorLog
                        ErrorLog.WARNING('Error importing token',
                                         str(e),
                                         transaction=tx['hash']
                                         )
                        scanlog.error('Error importing token %s' % e)
                        #count_metrics('scanner.token_import_error', {'network': self.network.nickname})
                        #count_metrics('scanner.timers.discover_token_error', {'network': self.network.nickname}, time.time() - token_timer, 'Seconds')
            #count_metrics('scanner.timers.whole_process', {'network': self.network.nickname}, time.time() - tx_timer, 'Seconds')
        count_metrics('scanner.process_transactions', {'network': self.network.nickname}, count)

    def __unicode__(self):
        return '%s @ %s' % (str(self), self.latest_block)

    @classmethod
    def MAIN(cls):
        return MAIN_SCANNER()

    @classmethod
    def ROPSTEN(cls):
        return ROPSTEN_SCANNER()

    @classmethod
    def TEST(cls):
        return TEST_SCANNER()

    def block_scan(self, start_block, end_block=None, timeout=10, update_latest=False, save_transactions=False, background=False):
        thread_number = int(random.random() * 10000)
        if not self.get_available_lock():
            scanlog.info('Duplicate blockscan, exiting: %s#%s' %
                         (self.network, thread_number))
            count_metrics('scanner.duplicate_blockscanner', {'network': self.network.nickname})
            return

        scanlog.info('Starting blockscan: %s#%s' %
                     (self.network, thread_number))
        start = time.time()
        end = start + timeout
        next_block = start_block
        while time.time() < end:
            elapsed = time.time() - start
            current_block = self.network.current_block()
            count_metrics('scanner.blocks_behind', {'network': self.network.nickname}, max(current_block - next_block, 0))
            if next_block > current_block:
                scanlog.info('Ending blockscan#%s [%s]: No more %s blocks!' % (
                    thread_number, elapsed, self.network))
                count_metrics('scanner.end_blockscan', {'network': self.network.nickname, 'reason': 'no_more_blocks'}, elapsed, 'Seconds')
                self.release_lock()
                return
            if end_block and next_block > end_block:
                scanlog.info('Ending blockscan#%s [%s]: Reached endblock!' % (
                    thread_number, elapsed))
                count_metrics('scanner.end_blockscan', {'network': self.network.nickname, 'reason': 'reached_endblock'}, elapsed, 'Seconds')
                self.release_lock()
                return

            if background:
                from .tasks import async_process_block
                async_process_block(self.id, next_block)
            else:
                self.process_block(next_block, save_transactions=save_transactions)

            if update_latest:
                self.latest_block = next_block
                self.save()

            next_block += 1

        elapsed = time.time() - start

        # Mail an admin if we run out of scanblock time
        scanlog.info('Ending blockscan#%s [%s]: Out of time!' % (
            thread_number, elapsed))
        count_metrics('scanner.end_blockscan', {'network': self.network.nickname, 'reason': 'out_of_time'}, elapsed, 'Seconds')
        self.release_lock()
        sys.exit()

    def scan_tail(self, timeout, background=False):
        return self.block_scan(self.latest_block + 1, timeout=timeout, update_latest=True, background=background)


def DEFAULT():
    ether = Software.ETHEREUM()
    return {
        'mainnet': Network.UNIQUE('Ethereum Mainnet',
                                  software=ether,
                                  endpoint=eth.WEB3_INFURA['main']
                                  ),
        'ropsten': Network.UNIQUE('Ethereum Ropsten',
                                  software=ether,
                                  endpoint=eth.WEB3_INFURA['ropsten']
                                  ),
    }


def MAIN_NETWORK():
    return DEFAULT()['mainnet']


def ROPSTEN_NETWORK():
    return DEFAULT()['ropsten']


def MAIN_SCANNER():
    main = MAIN_NETWORK()
    return Scanner.UNIQUE('PRIMARY - %s' % main.nickname, network=main)


def ROPSTEN_SCANNER():
    ropsten = ROPSTEN_NETWORK()
    return Scanner.UNIQUE('SECONDARY - %s' % ropsten.nickname, network=ropsten)


def TEST_SCANNER():
    main = MAIN_NETWORK()
    return Scanner.UNIQUE('TEST - %s' % main.nickname, network=main)
