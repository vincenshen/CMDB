# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-07-06 03:03
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Asset', '0010_auto_20170706_1013'),
    ]

    operations = [
        migrations.CreateModel(
            name='EventLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128, verbose_name='事件名称')),
                ('event_type', models.SmallIntegerField(choices=[(1, '硬件变更'), (2, '新增配件'), (3, '设备下线'), (4, '设备上线'), (5, '定期维护'), (6, '业务上线\\更新\\变更'), (7, '其它')], verbose_name='事件类型')),
                ('component', models.CharField(blank=True, max_length=128, null=True, verbose_name='事件子项')),
                ('detail', models.TextField(verbose_name='事件详情')),
                ('user', models.CharField(blank=True, max_length=32, null=True, verbose_name='事件处理人')),
                ('create_data', models.DateTimeField(auto_now_add=True)),
                ('asset', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Asset.Asset')),
            ],
            options={
                'verbose_name': '事件日志',
                'verbose_name_plural': '事件日志',
            },
        ),
        migrations.AlterField(
            model_name='newassetapprovalzone',
            name='asset_type',
            field=models.CharField(blank=True, choices=[('server', '服务器'), ('network', '网络设备'), ('storage', '存储设备'), ('security', '安全设备'), ('machineroom', '机房设备'), ('software', '软件资产'), ('others', '其他设备')], max_length=128, null=True),
        ),
    ]