# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('kaigi', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='meeting',
            name='organizer_email',
            field=models.CharField(default='example@example.com', max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='meeting',
            name='organizer_name',
            field=models.CharField(default='Example organizer', max_length=255),
            preserve_default=False,
        ),
    ]
