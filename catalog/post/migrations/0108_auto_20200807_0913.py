# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2020-08-07 09:13
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import django.db.models.manager


class Migration(migrations.Migration):

    dependencies = [
        ('file', '0011_auto_20200316_1949'),
        ('general', '0060_auto_20200327_0612'),
        ('post', '0107_auto_20200807_0910'),
    ]

    operations = [
        migrations.CreateModel(
            name='Article',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('published', models.BooleanField(default=False)),
                ('to_publish', models.BooleanField(default=True)),
                ('default_lang', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='general.Language')),
                ('image', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='article_image', to='file.UserImage')),
                ('image_draft', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='article_draft_image', to='file.UserImage')),
                ('post', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='article', to='post.Post')),
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
            name='ArticleTranslation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, max_length=500, null=True)),
                ('description', models.CharField(blank=True, max_length=500, null=True)),
                ('text', models.TextField(blank=True, null=True)),
                ('title_draft', models.CharField(blank=True, max_length=500, null=True)),
                ('description_draft', models.CharField(blank=True, max_length=500, null=True)),
                ('text_draft', models.TextField(blank=True, null=True)),
                ('language_code', models.CharField(db_index=True, max_length=15)),
                ('master', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='translations', to='post.Article')),
            ],
            options={
                'db_table': 'post_article_translation',
                'db_tablespace': '',
                'abstract': False,
                'managed': True,
                'default_permissions': (),
            },
        ),
        migrations.AlterUniqueTogether(
            name='articletranslation',
            unique_together=set([('language_code', 'master')]),
        ),
    ]
