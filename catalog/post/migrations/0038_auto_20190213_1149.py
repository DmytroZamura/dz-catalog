# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2019-02-13 11:49
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('post', '0037_auto_20190212_1308'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='categorypostfiltervalues',
            name='category',
        ),
        migrations.RemoveField(
            model_name='categorypostfiltervalues',
            name='city',
        ),
        migrations.RemoveField(
            model_name='categorypostfiltervalues',
            name='country',
        ),
        migrations.DeleteModel(
            name='CategoryPostFilterValues',
        ),
    ]
