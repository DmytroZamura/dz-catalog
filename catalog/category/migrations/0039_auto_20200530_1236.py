# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2020-05-30 12:36
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('category', '0038_auto_20200530_1228'),
    ]

    operations = [
        migrations.AlterField(
            model_name='categoryclassification',
            name='level1_code',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='categoryclassification',
            name='level2_code',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]