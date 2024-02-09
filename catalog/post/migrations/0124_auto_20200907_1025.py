# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2020-09-07 10:25
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('post', '0123_post_post_language'),
    ]

    operations = [
        migrations.AddField(
            model_name='articletranslation',
            name='link_canonical',
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='articletranslation',
            name='link_canonical_draft',
            field=models.URLField(blank=True, null=True),
        ),
    ]