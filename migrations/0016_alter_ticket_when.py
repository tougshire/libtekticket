# Generated by Django 3.2.9 on 2022-01-21 16:30

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('libtekticket', '0015_alter_ticket_options'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ticket',
            name='when',
            field=models.DateTimeField(default=datetime.date.today, help_text='The date and time the ticket was submitted'),
        ),
    ]
