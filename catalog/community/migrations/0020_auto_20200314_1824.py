# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2020-03-14 18:24
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0034_auto_20200223_1657'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('community', '0019_auto_20191218_1232'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='communityinvitation',
            unique_together=set([('company', 'community', 'user')]),
        ),
    ]