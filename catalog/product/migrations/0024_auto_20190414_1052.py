# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2019-04-14 10:52
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0023_auto_20190413_1308'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='link_to_buy',
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='producttranslation',
            name='packaging_and_delivery',
            field=models.TextField(blank=True, null=True),
        ),
    ]