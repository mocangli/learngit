# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-09-07 13:59
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0010_remove_review_filenumber'),
    ]

    operations = [
        migrations.AlterField(
            model_name='myfile',
            name='filenumber',
            field=models.CharField(max_length=50, verbose_name='图号'),
        ),
    ]
