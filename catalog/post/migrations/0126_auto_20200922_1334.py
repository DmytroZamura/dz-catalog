# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2020-09-22 13:34
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('post', '0125_auto_20200913_0858'),
    ]

    operations = [
        migrations.CreateModel(
            name='PostSEODataFollower',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('create_date', models.DateTimeField(auto_now_add=True)),
                ('data', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='followers', to='post.PostSEOData')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='followed_data', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='postseodatafollower',
            unique_together=set([('data', 'user')]),
        ),
    ]