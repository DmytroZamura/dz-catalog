# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-09-26 10:57
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('category', '0012_auto_20180925_0944'),
        ('user_profile', '0004_auto_20180925_1241'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofilecategories',
            name='profile_category',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterUniqueTogether(
            name='userprofilecategories',
            unique_together=set([('profile', 'category')]),
        ),
    ]
