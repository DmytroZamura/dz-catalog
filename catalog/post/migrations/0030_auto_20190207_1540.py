# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2019-02-07 15:40
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('general', '0024_auto_20181226_1321'),
        ('post', '0029_postattributevalue_value_list'),
    ]

    operations = [
        migrations.CreateModel(
            name='PostOffering',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.IntegerField(choices=[(1, '1. sales'), (2, '2. rent')], default=1)),
                ('city_name', models.CharField(blank=True, max_length=100, null=True)),
                ('price', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('city', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='general.City')),
                ('country', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='general.Country')),
                ('post', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='post_offering', to='post.Post')),
                ('price_currency', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='general.Currency')),
            ],
        ),
        migrations.RemoveField(
            model_name='postrequest',
            name='company',
        ),
        migrations.RemoveField(
            model_name='postrequest',
            name='details',
        ),
    ]
