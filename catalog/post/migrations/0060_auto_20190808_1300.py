# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2019-08-08 13:00
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.db.models.manager


class Migration(migrations.Migration):

    dependencies = [
        ('post', '0059_auto_20190801_1345'),
    ]

    operations = [
        migrations.CreateModel(
            name='ApplicantStatus',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=10, null=True, unique=True)),
                ('position', models.IntegerField(blank=True, null=True)),
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
            name='ApplicantStatusTranslation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=40)),
                ('language_code', models.CharField(db_index=True, max_length=15)),
                ('master', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='translations', to='post.ApplicantStatus')),
            ],
            options={
                'db_table': 'post_applicantstatus_translation',
                'db_tablespace': '',
                'abstract': False,
                'managed': True,
                'default_permissions': (),
            },
        ),
        migrations.RemoveField(
            model_name='applicant',
            name='approved',
        ),
        migrations.RemoveField(
            model_name='applicant',
            name='interview',
        ),
        migrations.RemoveField(
            model_name='applicant',
            name='rejected',
        ),
        migrations.AlterField(
            model_name='applicant',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='jobs', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='applicant',
            name='status',
            field=models.ForeignKey( null=True, on_delete=django.db.models.deletion.SET_NULL, to='post.ApplicantStatus'),
        ),
        migrations.AlterUniqueTogether(
            name='applicantstatustranslation',
            unique_together=set([('language_code', 'master')]),
        ),
    ]
