# Generated by Django 3.2.9 on 2022-01-22 11:34

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('libtekticket', '0018_auto_20220122_0525'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ticketnote',
            name='when',
            field=models.DateTimeField(default=datetime.datetime.now, help_text='The date that the note was submitted', verbose_name='when'),
        ),
    ]
