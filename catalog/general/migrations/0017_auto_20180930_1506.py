# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-09-30 15:06
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('general', '0016_auto_20180930_1448'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='UnitsType',
            new_name='UnitType',
        ),
        migrations.RenameModel(
            old_name='UnitsTypeTranslation',
            new_name='UnitTypeTranslation',
        ),
        migrations.AlterModelTable(
            name='unittypetranslation',
            table='general_unittype_translation',
        ),
    ]
