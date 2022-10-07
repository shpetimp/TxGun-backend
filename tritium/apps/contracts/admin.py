from django.contrib import admin
from .models import Contract, PriceLookup, ERC20

class ContractAdmin(admin.ModelAdmin):
    list_display = ['network', 'address']
admin.site.register(Contract, ContractAdmin)

class ERC20Admin(admin.ModelAdmin):
    list_display = ['symbol', 'nickname', 'decimal_places', 'contract']
admin.site.register(ERC20, ERC20Admin)

class PriceLookupAdmin(admin.ModelAdmin):
    list_display = ['created_at', 'asset', 'currency', 'price']
admin.site.register(PriceLookup, PriceLookupAdmin)