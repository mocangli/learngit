# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-09-07 13:19
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0009_auto_20160907_1304'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='review',
            name='filenumber',
        ),
    ]
