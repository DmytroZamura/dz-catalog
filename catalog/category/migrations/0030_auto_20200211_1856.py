# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2020-02-11 18:56
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('category', '0029_auto_20200211_1847'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='external_code',
            field=models.CharField(blank=True, max_length=15, null=True),
        ),
    ]
