from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tritium.conf')

app = Celery('tritium')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))


@app.task(bind=True)
def main_scanner(self):
    from scripts import main_scanner
    main_scanner.run()

@app.task(bind=True)
def midnight_job(self):
    from scripts import midnight_job
    midnight_job.run()

@app.task(bind=True)
def monthly_summary(self):
    from scripts import monthly_summary
    monthly_summary.run()

@app.task(bind=True)
def daily_summary(self):
    from scripts import daily_summary
    daily_summary.run()
