# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-01-31 18:44
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0019_auto_20160129_2140'),
    ]

    operations = [
        migrations.AlterField(
            model_name='person',
            name='preferred_name_display_style',
            field=models.CharField(blank=True, choices=[('firstname_nick_surname', 'Firstname "Nickname" Surname'), ('firstname_surname', 'Firstname Surname'), ('firstname', 'Firstname'), ('nick', 'Nickname')], help_text='T\xe4ss\xe4 voit vaikuttaa siihen, miss\xe4 muodossa nimesi esitet\xe4\xe4n (esim. painetaan badgeesi).', max_length=31, verbose_name='Nimen esitt\xe4minen'),
        ),
    ]
