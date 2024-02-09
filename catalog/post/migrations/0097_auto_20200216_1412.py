# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2020-02-16 14:12
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('category', '0034_auto_20200216_1358'),
        ('general', '0052_auto_20200107_1033'),
        ('post', '0096_post_is_video_url'),
    ]

    operations = [
        migrations.CreateModel(
            name='PostSEOData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='category.Category')),
                ('city', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='general.City')),
                ('country', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='general.Country')),
                ('job_function', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='general.JobFunction')),
                ('job_type', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='general.JobType')),
                ('post_type', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='post.PostType')),
                ('seniority', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='general.SeniorityLabel')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='postseodata',
            unique_together=set([('category', 'post_type', 'country', 'city', 'job_type', 'job_function', 'seniority')]),
        ),
    ]