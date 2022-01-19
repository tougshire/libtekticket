# Generated by Django 3.2.9 on 2022-01-18 11:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('libtekticket', '0012_ticketnote_submitted_by'),
    ]

    operations = [
        migrations.AddField(
            model_name='technician',
            name='is_current',
            field=models.BooleanField(default=True, help_text='If this technician is current (should receive emails from tickets, etc)', verbose_name='current'),
        ),
        migrations.AlterField(
            model_name='ticket',
            name='urgency',
            field=models.IntegerField(choices=[(1, '1) Safety Hazard or Work Stoppage'), (2, '2) Major Work Impediment'), (3, '3) Highly Important Issue'), (4, '4) Moderately Important Issue'), (5, '5) Minor Issue or Suggestion')], help_text='The urgency, on a scale of 1 to 5, where 1 is the most urgent', verbose_name='Urgency'),
        ),
    ]