# Generated by Django 2.0 on 2019-05-23 19:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('subscriptions', '0008_auto_20190522_2104'),
    ]

    operations = [
        migrations.RenameField(
            model_name='subscription',
            old_name='daily_notifications',
            new_name='daily_emails',
        ),
        migrations.RenameField(
            model_name='subscription',
            old_name='monthly_notifications',
            new_name='monthly_emails',
        ),
    ]
