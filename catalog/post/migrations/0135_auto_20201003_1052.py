# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2020-10-03 10:52
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('post', '0134_auto_20201002_0839'),
    ]

    operations = [
        migrations.CreateModel(
            name='PostUserEngagements',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('type', models.IntegerField(choices=[(1, '1. Link Click'), (2, '2. Respond'), (3, '3. ProfileClick')], default=1)),
                ('create_date', models.DateTimeField(auto_now_add=True)),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='engagements', to='post.Post')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='engagements', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='posteventsqty',
            name='engagements',
            field=models.PositiveIntegerField(default=0),
        ),
    ]