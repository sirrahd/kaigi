# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('kaigi', '0003_meetingassoc'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='session',
            unique_together=set([('person', 'meeting')]),
        ),
    ]
