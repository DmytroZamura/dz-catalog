# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2020-12-29 12:24
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0007_auto_20201225_1148'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='paymentorder',
            name='canceled',
        ),
        migrations.AlterField(
            model_name='paymentaccount',
            name='company',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='balance', to='company.Company'),
        ),
        migrations.AlterField(
            model_name='paymentaccount',
            name='user',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='balance', to=settings.AUTH_USER_MODEL),
        ),
    ]
