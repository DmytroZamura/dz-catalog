# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2019-02-08 16:37
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('post', '0033_auto_20190208_1634'),
    ]

    operations = [
        migrations.AlterField(
            model_name='postoffering',
            name='post',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='post_offering', to='post.Post'),
        ),
    ]
