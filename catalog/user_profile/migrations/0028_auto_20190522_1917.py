# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2019-05-22 19:17
from __future__ import unicode_literals

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('user_profile', '0027_userprofile_cognito_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='cognito_id',
            field=models.UUIDField(db_index=True, default=uuid.uuid4),
        ),
    ]