# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-12-10 12:06
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('employment', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofileemployment',
            name='company',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='employees', to='company.Company'),
        ),
        migrations.AlterField(
            model_name='userprofileemployment',
            name='profile',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='emlpoyment', to='user_profile.UserProfile'),
        ),
    ]