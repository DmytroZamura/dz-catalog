# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2019-02-07 11:26
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('post', '0027_auto_20190207_0917'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='postattributevalue',
            name='value_list',
        ),
    ]
