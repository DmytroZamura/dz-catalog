# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2019-12-26 14:56
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('general', '0050_auto_20191223_1631'),
    ]

    operations = [
        migrations.AlterField(
            model_name='city',
            name='region',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='region_cities', to='general.Region'),
        ),
    ]
