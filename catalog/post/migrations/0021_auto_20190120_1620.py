# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2019-01-20 16:20
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('post', '0020_auto_20190120_1600'),
    ]

    operations = [
        migrations.AlterField(
            model_name='postrequest',
            name='post',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='post_request', to='post.Post'),
        ),
    ]
