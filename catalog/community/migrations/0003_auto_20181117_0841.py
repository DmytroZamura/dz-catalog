# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-11-17 08:41
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('community', '0002_auto_20181117_0725'),
    ]

    operations = [
        migrations.AddField(
            model_name='communityinvitation',
            name='accepted_by_user',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='communityinvitation',
            name='user_acceptance',
            field=models.BooleanField(default=False),
        ),
    ]
