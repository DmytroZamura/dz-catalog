# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2021-01-06 12:10
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0013_payment_order_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='payment_id',
            field=models.BigIntegerField(blank=True, null=True),
        ),
    ]