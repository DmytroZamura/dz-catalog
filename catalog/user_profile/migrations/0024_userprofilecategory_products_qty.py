# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2019-04-11 09:41
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_profile', '0023_userprofile_img'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofilecategory',
            name='products_qty',
            field=models.IntegerField(default=0),
        ),
    ]
