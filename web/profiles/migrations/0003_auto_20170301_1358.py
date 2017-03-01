# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-03-01 13:58
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0002_auto_20170301_1329'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='user_type',
            field=models.SmallIntegerField(choices=[(0, 'Superuser'), (1, 'Moderator'), (2, 'Instructor'), (3, 'Participant')], default=3),
        ),
    ]
