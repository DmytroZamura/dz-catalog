# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2020-10-01 11:54
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('post', '0129_postfilterfeed_create_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='posteventsqty',
            name='impressions',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='posteventsqty',
            name='views',
            field=models.PositiveIntegerField(default=0),
        ),
    ]