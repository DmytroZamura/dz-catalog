# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2021-01-03 14:25
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0008_auto_20201229_1224'),
    ]

    operations = [
        migrations.AddField(
            model_name='paymentorder',
            name='payment_product',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='orders', to='payments.PaymentProduct'),
        ),
    ]