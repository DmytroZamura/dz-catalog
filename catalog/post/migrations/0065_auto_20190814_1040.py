# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2019-08-14 10:40
from __future__ import unicode_literals

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.db.models.manager


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('general', '0032_auto_20190719_1019'),
        ('file', '0008_auto_20190412_1542'),
        ('messaging', '0009_auto_20190724_1714'),
        ('post', '0064_auto_20190809_0912'),
    ]

    operations = [
        migrations.CreateModel(
            name='PostRespond',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('contact_email', models.CharField(blank=True, max_length=100, null=True)),
                ('contact_phone', models.CharField(blank=True, max_length=15, null=True)),
                ('skype', models.CharField(blank=True, max_length=50, null=True)),
                ('create_date', models.DateTimeField(auto_now_add=True)),
                ('update_date', models.DateTimeField(default=datetime.datetime.now)),
                ('reviewed', models.BooleanField(default=False, null=None)),
                ('cover_letter', models.TextField(blank=True, null=True)),
                ('comment', models.TextField(blank=True, null=True)),
                ('rating', models.PositiveIntegerField(default=0)),
                ('proposed_price', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='PostRespondDocument',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('file', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='file.File')),
            ],
        ),
        migrations.CreateModel(
            name='PostRespondStatus',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=10, null=True, unique=True)),
                ('position', models.IntegerField(blank=True, null=True)),
                ('icon', models.CharField(blank=True, max_length=40, null=True)),
                ('color_class', models.CharField(blank=True, max_length=20, null=True)),
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
            name='PostRespondStatusTranslation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=40)),
                ('language_code', models.CharField(db_index=True, max_length=15)),
                ('master', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='translations', to='post.PostRespondStatus')),
            ],
            options={
                'db_table': 'post_postrespondstatus_translation',
                'db_tablespace': '',
                'abstract': False,
                'managed': True,
                'default_permissions': (),
            },
        ),
        migrations.CreateModel(
            name='PostRespondChat',
            fields=[
                ('respond', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='chat', serialize=False, to='post.PostRespond')),
                ('chat', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='respond', to='messaging.Chat')),
            ],
        ),
        migrations.AddField(
            model_name='postresponddocument',
            name='respond',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='documents', to='post.PostRespond'),
        ),
        migrations.AddField(
            model_name='postrespond',
            name='company',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='company_responds', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='postrespond',
            name='currency',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='general.Currency'),
        ),
        migrations.AddField(
            model_name='postrespond',
            name='post',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='responds', to='post.Post'),
        ),
        migrations.AddField(
            model_name='postrespond',
            name='status',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='post.PostRespondStatus'),
        ),
        migrations.AddField(
            model_name='postrespond',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='user_responds', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterUniqueTogether(
            name='postrespondstatustranslation',
            unique_together=set([('language_code', 'master')]),
        ),
        migrations.AlterUniqueTogether(
            name='postrespond',
            unique_together=set([('post', 'user', 'company')]),
        ),
        migrations.AlterUniqueTogether(
            name='postrespondchat',
            unique_together=set([('respond', 'chat')]),
        ),
    ]