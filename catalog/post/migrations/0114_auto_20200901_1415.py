# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2020-09-01 14:15
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('post', '0113_remove_article_published'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='slug',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
    ]
