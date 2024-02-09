# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-11-29 08:56
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import django.db.models.manager


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0008_companycategory_child_qty'),
        ('user_profile', '0012_userprofilecategory_child_qty'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserProfileEmployment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('company_name', models.CharField(blank=True, max_length=100, null=True)),
                ('position', models.PositiveIntegerField(blank=True, null=True)),
                ('company', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='company.Company')),
            ],
            options={
                'abstract': False,
                'base_manager_name': '_plain_manager',
            },
            managers=[
                ('objects', django.db.models.manager.Manager()),
                ('_plain_manager', django.db.models.manager.Manager()),
            ],
        ),
        migrations.CreateModel(
            name='UserProfileEmploymentTranslation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, max_length=100, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('language_code', models.CharField(db_index=True, max_length=15)),
                ('master', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='translations', to='user_profile.UserProfileEmployment')),
            ],
            options={
                'db_table': 'user_profile_userprofileemployment_translation',
                'db_tablespace': '',
                'abstract': False,
                'managed': True,
                'default_permissions': (),
            },
        ),
        migrations.AddField(
            model_name='userprofile',
            name='contact_email',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='userprofileemployment',
            name='profile',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user_profile.UserProfile'),
        ),
        migrations.AlterUniqueTogether(
            name='userprofileemploymenttranslation',
            unique_together=set([('language_code', 'master')]),
        ),
    ]