# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2020-06-06 08:15
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('attribute', '0008_auto_20190212_1955'),
    ]

    operations = [
        migrations.CreateModel(
            name='AttributeClassification',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.CharField(blank=True, max_length=60, null=True)),
                ('attribute_name_en', models.CharField(max_length=40)),
                ('attribute_name_ru', models.CharField(max_length=40)),
                ('attribute_name_uk', models.CharField(max_length=40)),
                ('attribute_value_en', models.CharField(max_length=40)),
                ('attribute_value_ru', models.CharField(max_length=40)),
                ('attribute_value_uk', models.CharField(max_length=40)),
            ],
        ),
        migrations.AddField(
            model_name='attribute',
            name='slug',
            field=models.CharField(blank=True, max_length=60, null=True),
        ),
        migrations.AddField(
            model_name='attributeclassification',
            name='attribute',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='attribute.Attribute'),
        ),
        migrations.AddField(
            model_name='attributeclassification',
            name='attribute_value',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='attribute.AttributeValue'),
        ),
    ]
