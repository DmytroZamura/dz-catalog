# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2020-01-07 10:33
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_profile', '0045_auto_20191230_1232'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofiletranslation',
            name='full_name',
            field=models.CharField(blank=True, db_index=True, max_length=120, null=True),
        ),
    ]