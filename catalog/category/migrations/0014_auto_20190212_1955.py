# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2019-02-12 19:55
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('category', '0013_auto_20190206_1337'),
    ]

    operations = [
        migrations.AddField(
            model_name='categoryattribute',
            name='max',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='categoryattribute',
            name='min',
            field=models.PositiveIntegerField(blank=True, default=0, null=True),
        ),
        migrations.AddField(
            model_name='categoryattribute',
            name='step',
            field=models.PositiveIntegerField(blank=True, default=1, null=True),
        ),
    ]