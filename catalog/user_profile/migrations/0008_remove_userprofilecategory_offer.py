# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-09-26 12:41
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user_profile', '0007_auto_20180926_1235'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprofilecategory',
            name='offer',
        ),
    ]