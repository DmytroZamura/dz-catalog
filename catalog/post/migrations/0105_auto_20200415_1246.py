# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2020-04-15 12:46
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('post', '0104_auto_20200415_1243'),
    ]

    operations = [
        migrations.AlterField(
            model_name='postcommenturlpreview',
            name='url',
            field=models.URLField(blank=True, max_length=500, null=True),
        ),
    ]
