# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2020-09-02 08:48
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('post', '0117_article_draft_tags'),
    ]

    operations = [
        migrations.RenameField(
            model_name='article',
            old_name='draft_tags',
            new_name='tags',
        ),
    ]
