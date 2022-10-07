#from zappa.async import task

#@task
def async_process_block(scanner_id, block_number):
    from .models import Scanner
    Scanner.objects.get(pk=scanner_id).process_block(block_number)
