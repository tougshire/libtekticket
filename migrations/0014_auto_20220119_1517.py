# Generated by Django 3.2.9 on 2022-01-19 20:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('libtekticket', '0013_auto_20220118_0609'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ticket',
            name='resolution',
        ),
        migrations.AddField(
            model_name='ticket',
            name='is_resolved',
            field=models.BooleanField(blank=True, default=False, help_text='If the problem is resolved', verbose_name='is resolved'),
        ),
        migrations.AddField(
            model_name='ticket',
            name='resolution_notes',
            field=models.TextField(blank=True, help_text='How the problem was resolved', verbose_name='resolution notes'),
        ),
    ]
