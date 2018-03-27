# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2018-03-27 09:54
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0005_auto_20180323_0035'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sportshall',
            name='latitude',
            field=models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True),
        ),
        migrations.AlterField(
            model_name='sportshall',
            name='longitude',
            field=models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True),
        ),
    ]
