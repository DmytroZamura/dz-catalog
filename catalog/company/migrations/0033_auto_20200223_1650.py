# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2020-02-23 16:50
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0032_auto_20200217_1313'),
    ]

    operations = [
        migrations.CreateModel(
            name='IndustryClassification',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.CharField(blank=True, max_length=60, null=True, unique=True)),
                ('name_en', models.CharField(max_length=40)),
                ('name_ru', models.CharField(max_length=40)),
                ('name_uk', models.CharField(max_length=40)),
            ],
        ),
        migrations.AlterField(
            model_name='companyindustry',
            name='slug',
            field=models.CharField(blank=True, db_index=True, max_length=60, null=True, unique=True),
        ),
    ]
