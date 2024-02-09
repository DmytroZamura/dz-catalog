# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2019-02-28 10:02
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('post', '0043_auto_20190224_1302'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='shared_post',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='child_posts', to='post.Post'),
        ),
    ]
