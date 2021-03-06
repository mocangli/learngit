# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-09-06 14:52
from __future__ import unicode_literals

import app.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0004_review'),
    ]

    operations = [
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.CharField(default=app.models.next_id, max_length=50, primary_key=True, serialize=False)),
                ('review_id', models.CharField(max_length=50)),
                ('user_id', models.CharField(max_length=50)),
                ('user_name', models.CharField(max_length=50)),
                ('content', models.TextField()),
                ('created_at', models.DateField(auto_now_add=True, verbose_name='创建时间')),
            ],
        ),
    ]
