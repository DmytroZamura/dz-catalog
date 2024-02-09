# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2020-10-03 11:38
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('post', '0141_auto_20201003_1131'),
    ]

    operations = [
        migrations.AlterField(
            model_name='postuserengagement',
            name='type',
            field=models.IntegerField(choices=[(1, '1. Link Click'), (2, '2. Respond'), (3, '3. ProfileClick'), (4, '4. AddToFavorite'), (5, '5. ShowMore'), (6, '6. Vote'), (7, '7. ImagePreview')], default=1),
        ),
    ]