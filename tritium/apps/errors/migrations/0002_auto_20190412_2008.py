# Generated by Django 2.0 on 2019-04-12 20:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('errors', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='errorlog',
            name='level',
            field=models.CharField(default='exception', max_length=16),
        ),
        migrations.AddField(
            model_name='errorlog',
            name='transaction',
            field=models.TextField(blank=True, null=True),
        ),
    ]
