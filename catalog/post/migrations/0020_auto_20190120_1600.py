# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2019-01-20 16:00
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('post', '0019_auto_20190120_1553'),
    ]

    operations = [
        migrations.AlterField(
            model_name='postrequest',
            name='post',
            field=models.OneToOneField(blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='post_request', to='post.Post'),
        ),
    ]