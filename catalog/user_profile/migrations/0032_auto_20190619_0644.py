# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2019-06-19 06:44
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user_profile', '0031_auto_20190612_1121'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='usercontact',
            unique_together=set([]),
        ),
        migrations.RemoveField(
            model_name='usercontact',
            name='contact',
        ),
        migrations.RemoveField(
            model_name='usercontact',
            name='user',
        ),
        migrations.DeleteModel(
            name='UserContact',
        ),
    ]
