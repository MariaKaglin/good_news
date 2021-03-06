# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-06-05 11:59
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('my_admin', '0002_auto_20170605_0610'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.RemoveField(
            model_name='news',
            name='id',
        ),
        migrations.AddField(
            model_name='news',
            name='news_id',
            field=models.CharField(default=0, max_length=200, primary_key=True, serialize=False),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='userprofile',
            name='news',
            field=models.ManyToManyField(to='my_admin.News'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
