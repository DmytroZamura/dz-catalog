# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-09-25 07:59
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('category', '0008_auto_20180924_1430'),
    ]

    operations = [
        migrations.AddField(
            model_name='categorytranslation',
            name='name_with_parent',
            field=models.CharField(default=1, max_length=120),
            preserve_default=False,
        ),
    ]
