# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2020-12-22 13:46
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import django.db.models.manager


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('general', '0061_auto_20200910_1246'),
    ]

    operations = [
        migrations.CreateModel(
            name='PaymentProduct',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(db_index=True, max_length=60, unique=True)),
                ('unit_type', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='general.UnitType')),
            ],
            options={
                'ordering': ['code'],
            },
            managers=[
                ('objects', django.db.models.manager.Manager()),
                ('_plain_manager', django.db.models.manager.Manager()),
            ],
        ),
        migrations.CreateModel(
            name='PaymentProductTranslation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True, null=True)),
                ('language_code', models.CharField(db_index=True, max_length=15)),
                ('master', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='translations', to='payments.PaymentProduct')),
            ],
            options={
                'db_table': 'payments_paymentproduct_translation',
                'db_tablespace': '',
                'abstract': False,
                'managed': True,
                'default_permissions': (),
            },
        ),
        migrations.AlterUniqueTogether(
            name='paymentproducttranslation',
            unique_together=set([('language_code', 'master')]),
        ),
    ]