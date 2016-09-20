# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('kaigi', '0004_auto_20150729_2310'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chat',
            name='text',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='chat',
            name='username',
            field=models.CharField(max_length=255),
        ),
    ]
