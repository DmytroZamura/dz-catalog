# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2019-10-06 14:16
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('post', '0079_auto_20191005_1639'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='multi_selection',
            field=models.BooleanField(default=False),
        ),
    ]
