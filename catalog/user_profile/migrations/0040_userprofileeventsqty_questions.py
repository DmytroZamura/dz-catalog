# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2019-10-05 17:33
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_profile', '0039_auto_20191003_0726'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofileeventsqty',
            name='questions',
            field=models.PositiveIntegerField(default=0),
        ),
    ]