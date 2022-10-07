from django.contrib import admin
from .models import Subscription, SubscribedTransaction

admin.site.register(Subscription)
admin.site.register(SubscribedTransaction)