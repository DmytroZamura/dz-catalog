# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2019-04-21 10:00
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('taggit', '0003_taggeditem_add_unique_index'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='TagFollower',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
            ],
        ),
        migrations.CreateModel(
            name='TagQty',
            fields=[
                ('tag', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='qty', serialize=False, to='taggit.Tag')),
                ('followers', models.PositiveIntegerField(default=0)),
            ],
        ),
        migrations.AddField(
            model_name='tagfollower',
            name='tag',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='taggit.Tag'),
        ),
        migrations.AddField(
            model_name='tagfollower',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterUniqueTogether(
            name='tagfollower',
            unique_together=set([('tag', 'user')]),
        ),
    ]