from .utils import safe_script
import logging
scanlog = logging.getLogger('scanner')

@safe_script
def run():
    print('Starting up Main Scanner Script')
    from tritium.apps.networks.models import Scanner
    scanner = Scanner.MAIN()
    scanner.scan_tail(timeout=110, background=True)
