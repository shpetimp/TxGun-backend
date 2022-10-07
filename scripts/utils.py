import traceback

def safe_script(func):
    def script():
        try:
            func()
        except Exception as e:
            traceback.print_exc()
            from tritium.apps.errors.models import ErrorLog
            ErrorLog.objects.create(nickname=str(e),
                                    traceback=traceback.format_exc())
    return script
