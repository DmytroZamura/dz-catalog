# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2020-02-11 18:47
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('category', '0028_auto_20200210_1937'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='updated',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='category',
            name='default_name',
            field=models.CharField(blank=True, max_length=150),
        ),
        migrations.AlterField(
            model_name='categorytranslation',
            name='name',
            field=models.CharField(max_length=150),
        ),
    ]