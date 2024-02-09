# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2019-11-05 15:28
from __future__ import unicode_literals

from django.db import migrations
import sorl.thumbnail.fields


class Migration(migrations.Migration):

    dependencies = [
        ('category', '0018_category_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='background_image',
            field=sorl.thumbnail.fields.ImageField(blank=True, null=True, upload_to='%Y/%m/%d/'),
        ),
    ]