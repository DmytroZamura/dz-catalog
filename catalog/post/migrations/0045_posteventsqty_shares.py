# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2019-02-28 10:20
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('post', '0044_post_shared_post'),
    ]

    operations = [
        migrations.AddField(
            model_name='posteventsqty',
            name='shares',
            field=models.PositiveIntegerField(default=0),
        ),
    ]