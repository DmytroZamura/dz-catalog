# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-10-16 11:13
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0005_auto_20181012_1051'),
    ]

    operations = [
        migrations.AddField(
            model_name='productimage',
            name='description',
            field=models.CharField(blank=True, max_length=350, null=True),
        ),
        migrations.AddField(
            model_name='productimage',
            name='title',
            field=models.CharField(blank=True, max_length=80, null=True),
        ),
    ]