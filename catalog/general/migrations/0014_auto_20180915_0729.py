# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-09-15 07:29
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('general', '0013_auto_20180915_0728'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='language',
            options={'base_manager_name': '_plain_manager'},
        ),
    ]