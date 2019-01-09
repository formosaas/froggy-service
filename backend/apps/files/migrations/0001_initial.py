# Generated by Django 2.1.5 on 2019-01-10 10:10

import apps.files.storages
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('cases', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CaseFile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(storage=apps.files.storages.PrivateStorage(bucket='mlozo-case'), upload_to='', verbose_name='Case File')),
                ('file_name', models.CharField(blank=True, editable=False, max_length=255, null=True, verbose_name='Case File Name')),
                ('upload_time', models.DateTimeField(auto_now=True, verbose_name='Upload Time')),
                ('case', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='casefile', to='cases.Case', verbose_name='Case File')),
            ],
        ),
        migrations.CreateModel(
            name='TempFile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('case', models.CharField(max_length=255, verbose_name='Temp Case')),
                ('file', models.FileField(upload_to='', verbose_name='Temp file')),
                ('file_name', models.CharField(blank=True, editable=False, max_length=255, null=True, verbose_name='Temp File Name')),
                ('size', models.PositiveIntegerField(editable=False, verbose_name='Size')),
                ('upload_time', models.DateTimeField(auto_now=True, verbose_name='Upload Time')),
            ],
        ),
    ]