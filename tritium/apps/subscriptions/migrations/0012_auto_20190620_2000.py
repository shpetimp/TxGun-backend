# Generated by Django 2.0 on 2019-06-20 20:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('subscriptions', '0011_subscription_weekly_emails'),
    ]

    operations = [
        migrations.AddField(
            model_name='subscription',
            name='low_balance_warning',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='subscription',
            name='notify_email',
            field=models.CharField(blank=True, max_length=512, null=True),
        ),
    ]
