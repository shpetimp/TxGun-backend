from .utils import safe_script
import logging
scanlog = logging.getLogger('scanner')
from django.core.mail import EmailMessage
import json
from datetime import datetime, timedelta
import csv
from io import StringIO
from tritium.apps.users.models import CustomUser as User

@safe_script
def run():
    for user in User.objects.all():
        #user.add_monthly_credit()
        user.low_credit_balance_email()
    