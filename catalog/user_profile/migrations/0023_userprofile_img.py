# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2019-04-09 18:50
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('file', '0007_auto_20190409_1150'),
        ('user_profile', '0022_remove_userprofile_img'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='img',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='file.UserImage'),
        ),
    ]
