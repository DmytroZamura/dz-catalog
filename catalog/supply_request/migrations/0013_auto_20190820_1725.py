# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2019-08-20 17:25
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('supply_request', '0011_auto_20190819_1748'),
    ]

    operations = [
        migrations.AddField(
            model_name='supplyrequest',
            name='contact_email',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='supplyrequest',
            name='contact_phone',
            field=models.CharField(blank=True, max_length=15, null=True),
        ),
        migrations.AddField(
            model_name='supplyrequest',
            name='skype',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]