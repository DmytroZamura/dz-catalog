# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2019-07-29 11:36
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('post', '0055_auto_20190725_1206'),
    ]

    operations = [
        migrations.AddField(
            model_name='postjob',
            name='resume_required',
            field=models.BooleanField(default=False),
        ),
    ]
