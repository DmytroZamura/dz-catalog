# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2019-12-19 16:46
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('general', '0036_country_geoname_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='country',
            name='slug',
            field=models.CharField(blank=True, max_length=40, null=True),
        ),
    ]
