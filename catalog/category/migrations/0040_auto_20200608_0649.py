# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2020-06-08 06:49
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('category', '0039_auto_20200530_1236'),
    ]

    operations = [
        migrations.AddField(
            model_name='categoryattribute',
            name='position',
            field=models.IntegerField(db_index=True, default=0),
        ),
        migrations.AlterField(
            model_name='category',
            name='position',
            field=models.IntegerField(db_index=True, default=0),
        ),
    ]
