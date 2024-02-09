# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-10-11 11:23
from __future__ import unicode_literals

import autoslug.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user_profile', '0008_remove_userprofilecategory_offer'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='slug',
            field=autoslug.fields.AutoSlugField(default='nickname', editable=False, populate_from='nickname'),
            preserve_default=False,
        ),
    ]
