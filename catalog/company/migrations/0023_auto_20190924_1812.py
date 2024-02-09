# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2019-09-24 18:12
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('company', '0022_auto_20190902_1318'),
    ]

    operations = [
        migrations.CreateModel(
            name='FavoriteCompany',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('create_date', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.AddField(
            model_name='company',
            name='deleted',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='favoritecompany',
            name='company',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='company.Company'),
        ),
        migrations.AddField(
            model_name='favoritecompany',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterUniqueTogether(
            name='favoritecompany',
            unique_together=set([('user', 'company')]),
        ),
    ]
