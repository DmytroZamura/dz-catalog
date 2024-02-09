# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2019-02-21 11:33
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('file', '0005_auto_20190221_0725'),
        ('post', '0039_auto_20190221_0739'),
    ]

    operations = [
        migrations.CreateModel(
            name='PostComment',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('text', models.CharField(max_length=1000, null=True)),
                ('create_date', models.DateTimeField(auto_now_add=True)),
                ('update_date', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='PostCommentLike',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('create_date', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='PostEventsQty',
            fields=[
                ('post', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='eventsqty', serialize=False, to='post.Post')),
                ('comments', models.PositiveIntegerField(default=0)),
                ('likes', models.PositiveIntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='PostCommentEventsQty',
            fields=[
                ('comment', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='eventssqty', serialize=False, to='post.PostComment')),
                ('likes', models.PositiveIntegerField(default=0)),
                ('comments', models.PositiveIntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='PostCommentUrlPreview',
            fields=[
                ('comment', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='urlpreview', serialize=False, to='post.PostComment')),
                ('url', models.URLField(blank=True, null=True)),
                ('image', models.CharField(blank=True, max_length=1000, null=True)),
                ('title', models.CharField(blank=True, max_length=300, null=True)),
                ('description', models.CharField(blank=True, max_length=500, null=True)),
            ],
        ),
        migrations.AddField(
            model_name='postcommentlike',
            name='comment',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='post.PostComment'),
        ),
        migrations.AddField(
            model_name='postcommentlike',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='postcomment',
            name='image',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='file.File'),
        ),
        migrations.AddField(
            model_name='postcomment',
            name='parent',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='child_comments', to='post.PostComment'),
        ),
        migrations.AddField(
            model_name='postcomment',
            name='post',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='post.Post'),
        ),
        migrations.AddField(
            model_name='postcomment',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterUniqueTogether(
            name='postcommentlike',
            unique_together=set([('user', 'comment')]),
        ),
    ]