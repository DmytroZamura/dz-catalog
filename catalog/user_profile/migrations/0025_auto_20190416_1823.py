# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2019-04-16 18:23
from __future__ import unicode_literals

import autoslug.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user_profile', '0024_userprofilecategory_products_qty'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='slug',
            field=autoslug.fields.AutoSlugField(editable=True, populate_from='nickname', unique=True),
        ),
    ]