from .utils import safe_script
import logging
scanlog = logging.getLogger('scanner')

@safe_script
def run():
    scanlog.info('Starting up Ropsten Scanner Script')
    from tritium.apps.networks.models import Scanner
    scanner = Scanner.ROPSTEN()
    scanner.scan_tail(timeout=110, background=True)
