# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2020-09-06 10:29
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('post', '0119_auto_20200902_1007'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='allow_index',
            field=models.BooleanField(default=True),
        ),
    ]