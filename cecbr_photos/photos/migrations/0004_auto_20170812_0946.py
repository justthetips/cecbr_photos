# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-08-12 13:46
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('photos', '0003_auto_20170811_0641'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='album',
            options={'ordering': ['season', '-date'], 'verbose_name': 'Album', 'verbose_name_plural': 'Albums'},
        ),
        migrations.AddField(
            model_name='photo',
            name='analyzed_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='photo',
            name='downloaded',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='photo',
            name='found_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
