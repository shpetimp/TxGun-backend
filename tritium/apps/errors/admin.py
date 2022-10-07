from django.contrib import admin
from .models import ErrorLog
from django.utils.text import mark_safe

class ErrorLogAdmin(admin.ModelAdmin):
    def transaction_link(self, obj):
        if not obj.transaction:
            return ''
        url = 'https://etherscan.io/tx/%s' % obj.transaction 
        return mark_safe('<a href=%s>%s</a>' %(url, obj.transaction))

    list_display = ['created_at', 'level', 'nickname', 'traceback', 'transaction_link']
admin.site.register(ErrorLog, ErrorLogAdmin)
