from .utils import safe_script
@safe_script
def run():
    from tritium.apps.networks.models import Scanner
    scanner = Scanner.TEST()
    scanner.latest_block = 4999999
    scanner.save()
    scanner.block_scan(5000015, timeout=3, save_transactions=True)
