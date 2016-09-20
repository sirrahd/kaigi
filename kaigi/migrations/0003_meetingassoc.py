# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('kaigi', '0002_auto_20150728_1457'),
    ]

    operations = [
        migrations.CreateModel(
            name='MeetingAssoc',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('meeting', models.ForeignKey(to='kaigi.Meeting')),
                ('person', models.ForeignKey(to='kaigi.Person')),
            ],
        ),
    ]
