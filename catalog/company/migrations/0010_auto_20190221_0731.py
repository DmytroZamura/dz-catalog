# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2019-02-21 07:31
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0009_auto_20181210_1206'),
    ]

    operations = [
        migrations.AlterField(
            model_name='companycategory',
            name='id',
            field=models.BigAutoField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='companyfollower',
            name='id',
            field=models.BigAutoField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='companyuser',
            name='id',
            field=models.BigAutoField(primary_key=True, serialize=False),
        ),
    ]
