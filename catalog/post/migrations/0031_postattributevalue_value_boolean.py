# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2019-02-07 19:24
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('post', '0030_auto_20190207_1540'),
    ]

    operations = [
        migrations.AddField(
            model_name='postattributevalue',
            name='value_boolean',
            field=models.BooleanField(default=False),
        ),
    ]
