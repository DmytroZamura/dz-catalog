# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-09-14 21:46
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('general', '0009_auto_20180914_2127'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='country',
            options={'base_manager_name': '_plain_manager'},
        ),
    ]
