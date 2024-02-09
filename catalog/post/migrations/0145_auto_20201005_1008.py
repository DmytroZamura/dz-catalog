# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2020-10-05 10:08
from __future__ import unicode_literals

import catalog.post.models
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('post', '0144_auto_20201005_0928'),
    ]

    operations = [
        migrations.AlterField(
            model_name='postuserengagement',
            name='timestamp',
            field=models.CharField(default=catalog.post.models.get_date, max_length=20),
        ),
        migrations.AlterField(
            model_name='postuserimpression',
            name='timestamp',
            field=models.CharField(default=catalog.post.models.get_date, max_length=20),
        ),
        migrations.AlterUniqueTogether(
            name='postuserimpression',
            unique_together=set([('post', 'user', 'view', 'impression', 'timestamp')]),
        ),
    ]