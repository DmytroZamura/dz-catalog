# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-12-30 10:59
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('file', '0003_auto_20180911_1751'),
    ]

    operations = [
        migrations.AlterField(
            model_name='file',
            name='type',
            field=models.CharField(blank=True, max_length=200),
        ),
    ]
