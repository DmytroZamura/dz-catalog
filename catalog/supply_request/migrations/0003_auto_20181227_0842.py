# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-12-27 08:42
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('file', '0003_auto_20180911_1751'),
        ('product', '0015_auto_20181104_1652'),
        ('supply_request', '0002_auto_20181227_0838'),
    ]

    operations = [
        migrations.AlterField(
            model_name='supplyrequest',
            name='currency',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='general.Currency'),
        ),
        migrations.AlterField(
            model_name='supplyrequest',
            name='customer_company',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='customer_company_requests', to='company.Company'),
        ),
        migrations.AlterField(
            model_name='supplyrequest',
            name='customer_user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='customer_user_requests', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='supplyrequest',
            name='supplier_company',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='supplier_company_requests', to='company.Company'),
        ),
        migrations.AlterField(
            model_name='supplyrequest',
            name='supplier_user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='supplier_user_requests', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='supplyrequestdocument',
            name='file',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='file.File'),
        ),
        migrations.AlterField(
            model_name='supplyrequestnote',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='supplyrequestposition',
            name='product',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='product.Product'),
        ),
        migrations.AlterUniqueTogether(
            name='supplyrequestdocument',
            unique_together=set([('supply_request', 'file')]),
        ),
        migrations.AlterUniqueTogether(
            name='supplyrequestposition',
            unique_together=set([('supply_request', 'product')]),
        ),
    ]
