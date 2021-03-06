# Generated by Django 3.2.9 on 2021-12-26 10:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('libtekticket', '0004_auto_20211225_1639'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ticket',
            name='technician',
            field=models.ForeignKey(blank=True, help_text='The technician responsible for responding to this ticket', null=True, on_delete=django.db.models.deletion.SET_NULL, to='libtekticket.technician', verbose_name='technician'),
        ),
    ]
