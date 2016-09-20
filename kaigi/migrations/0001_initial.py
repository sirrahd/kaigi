# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Chat',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('username', models.CharField(max_length=100)),
                ('text', models.CharField(max_length=140)),
                ('time', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Meeting',
            fields=[
                ('id', models.UUIDField(serialize=False, editable=False, primary_key=True)),
                ('subject', models.CharField(max_length=255)),
                ('location', models.CharField(max_length=255)),
                ('start', models.DateTimeField()),
                ('end', models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name='Person',
            fields=[
                ('id', models.UUIDField(serialize=False, editable=False, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('last_login', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Rating',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('time', models.DateTimeField(auto_now_add=True)),
                ('rating', models.IntegerField()),
                ('meeting', models.ForeignKey(to='kaigi.Meeting')),
            ],
        ),
        migrations.CreateModel(
            name='Session',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('last_activity', models.DateTimeField(auto_now=True)),
                ('rating', models.IntegerField()),
                ('username', models.CharField(max_length=100)),
                ('meeting', models.ForeignKey(to='kaigi.Meeting')),
                ('person', models.ForeignKey(to='kaigi.Person')),
            ],
        ),
        migrations.AddField(
            model_name='chat',
            name='meeting',
            field=models.ForeignKey(to='kaigi.Meeting'),
        ),
    ]
