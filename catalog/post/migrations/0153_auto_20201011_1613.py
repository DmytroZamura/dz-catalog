# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2020-10-11 16:13
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('post', '0152_auto_20201011_1611'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='relatedpost',
            unique_together=set([('post', 'related_post')]),
        ),
    ]