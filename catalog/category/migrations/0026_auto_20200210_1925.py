# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2020-02-10 19:25
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('category', '0025_auto_20200210_1918'),
    ]

    operations = [
        migrations.AlterField(
            model_name='categoryclassification',
            name='livel3_code',
            field=models.CharField(blank=True, max_length=15, null=True),
        ),
        migrations.AlterField(
            model_name='categoryclassification',
            name='livel3_en_name',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='categoryclassification',
            name='livel3_ru_name',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='categoryclassification',
            name='livel3_uk_name',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='categoryclassification',
            name='livel4_code',
            field=models.CharField(blank=True, max_length=15, null=True),
        ),
        migrations.AlterField(
            model_name='categoryclassification',
            name='livel4_en_name',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='categoryclassification',
            name='livel4_ru_name',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='categoryclassification',
            name='livel4_uk_name',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='categoryclassification',
            name='livel5_code',
            field=models.CharField(blank=True, max_length=15, null=True),
        ),
        migrations.AlterField(
            model_name='categoryclassification',
            name='livel5_en_name',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='categoryclassification',
            name='livel5_ru_name',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='categoryclassification',
            name='livel5_uk_name',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='categoryclassification',
            name='livel6_code',
            field=models.CharField(blank=True, max_length=15, null=True),
        ),
        migrations.AlterField(
            model_name='categoryclassification',
            name='livel6_en_name',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='categoryclassification',
            name='livel6_ru_name',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='categoryclassification',
            name='livel6_uk_name',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
