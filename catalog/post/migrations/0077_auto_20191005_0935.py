# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2019-10-05 09:35
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('post', '0076_postoption_position'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='postoption',
            options={'ordering': ['position']},
        ),
    ]
