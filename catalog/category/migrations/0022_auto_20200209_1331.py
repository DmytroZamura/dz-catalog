# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2020-02-09 13:31
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('category', '0021_category_default_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='default_name',
            field=models.CharField(blank=True, max_length=60),
        ),
    ]
