# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-09-15 07:27
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('general', '0011_language_test'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='language',
            options={'ordering': ('name',)},
        ),
    ]
