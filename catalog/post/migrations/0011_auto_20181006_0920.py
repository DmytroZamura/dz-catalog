# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-10-06 09:20
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('post', '0010_posttype_position'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='comment',
            field=models.CharField(blank=True, max_length=2500, null=True),
        ),
    ]