from .utils import safe_script
import logging
from tritium.apps.subscriptions.models import Subscription, SubscribedTransaction
from tritium.apps.subscriptions.serializers import SubscribedTransactionSerializer
scanlog = logging.getLogger('scanner')
from django.core.mail import EmailMessage
import json
from datetime import datetime, timedelta
import csv
from io import StringIO
from django.conf import settings

@safe_script
def run():
    yesterday = datetime.utcnow()-timedelta(days=1)
    daily_summaries_enabled = Subscription.objects.filter(daily_emails=True)
    
    for subscription in daily_summaries_enabled:
        if subscription.daily_emails == True and subscription.user.subtract_credit(
            settings.DAILY_SUMMARY_CREDIT_COST, 'Daily Summary'):
            summary = [SubscribedTransactionSerializer(s).data
                    for s in subscription.transactions.filter(
                        created_at__gte=yesterday)]

        if not len(summary):
            continue
        csvfile = StringIO()
        fieldnames = list(summary[0].keys())
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for tx in summary:
            writer.writerow(tx)
        
        email = EmailMessage(
            '%s: Daily Summary' % subscription.nickname,
            'Attached as csv',
            'noreply@txgun.io',
            [subscription.user.email],
        )
        email.attach('file.csv', csvfile.getvalue(), 'text/csv')
        email.send()
        

            

