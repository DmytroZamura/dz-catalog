# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2020-04-01 14:17
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_profile', '0046_auto_20200107_1033'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='message_sound',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='notifications_sound',
            field=models.BooleanField(default=True),
        ),
    ]
