# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2020-08-07 12:40
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('general', '0060_auto_20200327_0612'),
        ('category', '0040_auto_20200608_0649'),
        ('post', '0109_auto_20200807_0929'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='draft_category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='category.Category'),
        ),
        migrations.AddField(
            model_name='article',
            name='draft_city',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='general.City'),
        ),
        migrations.AddField(
            model_name='article',
            name='draft_country',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='general.Country'),
        ),
        migrations.AlterField(
            model_name='post',
            name='community',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='community_posts', to='community.Community'),
        ),
    ]
