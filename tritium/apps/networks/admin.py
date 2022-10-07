from django.contrib import admin
from .models import Network, Software, Scanner

class ScannerAdmin(admin.ModelAdmin):
    list_display = ('nickname', 'latest_block')


admin.site.register(Network)
admin.site.register(Software)
admin.site.register(Scanner, ScannerAdmin)
