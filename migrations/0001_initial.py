# Generated by Django 3.2.9 on 2021-12-21 18:39

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('libtekin', '0003_auto_20211218_2007'),
    ]

    operations = [
        migrations.CreateModel(
            name='Technician',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, help_text='The name of the technician', max_length=50, verbose_name='name')),
                ('user', models.ForeignKey(help_text='The user account associated with this technician', null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='user')),
            ],
        ),
        migrations.CreateModel(
            name='TicketNote',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField(help_text='The text of the note', verbose_name='text')),
                ('when', models.DateField(default=datetime.date.today, help_text='The effective date of the note (when it applies as opposed to when it was actually made)', verbose_name='when')),
            ],
        ),
        migrations.CreateModel(
            name='Ticket',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.TextField(blank=True, help_text='The description of the problem', verbose_name='Description')),
                ('urgency', models.IntegerField(choices=[(1, 'Safety Hazard or Work Stoppage'), (2, ''), (3, 'Important Issue'), (4, ''), (5, 'Minor Issue or Suggestion')], help_text='The urgency, on a scale of 1 to 5, where 1 is the most urgent', verbose_name='Urgency')),
                ('item', models.ForeignKey(blank=True, help_text='The item to which this ticket applies', null=True, on_delete=django.db.models.deletion.SET_NULL, to='libtekin.item')),
                ('submitted_by', models.ForeignKey(help_text='The user who submitted this ticket', null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='submitted by')),
                ('technician', models.ForeignKey(help_text='The technician responsible for responding to this ticket', null=True, on_delete=django.db.models.deletion.SET_NULL, to='libtekticket.technician', verbose_name='technician')),
            ],
        ),
    ]
