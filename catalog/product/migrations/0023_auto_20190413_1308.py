# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2019-04-13 13:08
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0022_productattribute_productattributevalue'),
    ]

    operations = [
        migrations.RenameField(
            model_name='productattributevalue',
            old_name='post_attribute',
            new_name='product_attribute',
        ),
    ]
