# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2019-02-05 18:48
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('post', '0024_auto_20190127_1725'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='post_title',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
    ]