# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-07-04 03:40
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Asset', '0003_auto_20170704_1112'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='newassetapprovalzone',
            name='ram_size',
        ),
        migrations.AlterField(
            model_name='newassetapprovalzone',
            name='create_date',
            field=models.DateTimeField(auto_now_add=True, verbose_name='汇报日期'),
        ),
    ]
