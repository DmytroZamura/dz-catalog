# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-09-15 12:09
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('general', '0014_auto_20180915_0729'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='language',
            name='test',
        ),
        migrations.AddField(
            model_name='language',
            name='locale_lang',
            field=models.BooleanField(default=False),
        ),
    ]
