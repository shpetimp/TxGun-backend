# Generated by Django 2.0 on 2019-05-21 16:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_customuser_default_notify_url'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='apicredit',
            options={'ordering': ('-created_at',)},
        ),
        migrations.AlterModelOptions(
            name='apikey',
            options={'ordering': ('-created_at',)},
        ),
    ]