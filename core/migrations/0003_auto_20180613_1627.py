# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-06-13 19:27
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_auto_20180613_1505'),
    ]

    operations = [
        migrations.AlterField(
            model_name='document',
            name='document',
            field=models.FileField(upload_to='media/%Y/%m/%d/'),
        ),
    ]
