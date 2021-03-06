# Generated by Django 3.2.9 on 2021-12-27 15:53

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('libtekticket', '0007_ticket_short_description'),
    ]

    operations = [
        migrations.AlterField(
            model_name='technician',
            name='user',
            field=models.ForeignKey(blank=True, help_text='The user account associated with this technician', null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='user'),
        ),
    ]
