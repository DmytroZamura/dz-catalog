# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2020-11-23 15:35
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0045_auto_20200913_0858'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='productimage',
            options={'ordering': ['-id']},
        ),
    ]