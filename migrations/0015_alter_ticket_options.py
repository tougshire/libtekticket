# Generated by Django 3.2.9 on 2022-01-21 11:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('libtekticket', '0014_auto_20220119_1517'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='ticket',
            options={'ordering': ['-when', 'urgency']},
        ),
    ]