# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2020-12-24 10:33
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0004_paymentorder'),
    ]

    operations = [
        migrations.AddField(
            model_name='paymentorder',
            name='canceled',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='paymentorder',
            name='id',
            field=models.BigAutoField(primary_key=True, serialize=False),
        ),
    ]
