# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2019-02-21 16:05
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0018_auto_20190221_0740'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productgroupitem',
            name='id',
            field=models.BigAutoField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='productimage',
            name='id',
            field=models.BigAutoField(primary_key=True, serialize=False),
        ),
    ]