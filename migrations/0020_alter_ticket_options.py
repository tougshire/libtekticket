# Generated by Django 3.2.9 on 2022-02-04 17:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('libtekticket', '0019_alter_ticketnote_when'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='ticket',
            options={'ordering': ['is_resolved', '-when', 'urgency']},
        ),
    ]
