# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2020-07-03 10:43
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('attribute', '0011_attribute_updated'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attributeclassification',
            name='attribute_value_en',
            field=models.CharField(blank=True, max_length=40, null=True),
        ),
        migrations.AlterField(
            model_name='attributeclassification',
            name='attribute_value_ru',
            field=models.CharField(blank=True, max_length=40, null=True),
        ),
        migrations.AlterField(
            model_name='attributeclassification',
            name='attribute_value_uk',
            field=models.CharField(blank=True, max_length=40, null=True),
        ),
    ]
