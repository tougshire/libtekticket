# Generated by Django 3.2.9 on 2021-12-22 01:49

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('libtekticket', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='History',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('when', models.DateTimeField(auto_now_add=True, help_text='The date this change was made', verbose_name='when')),
                ('modelname', models.CharField(help_text='The model to which this change applies', max_length=50, verbose_name='model')),
                ('objectid', models.BigIntegerField(blank=True, help_text='The id of the record that was changed', null=True, verbose_name='object id')),
                ('fieldname', models.CharField(help_text='The that was changed', max_length=50, verbose_name='field')),
                ('old_value', models.TextField(blank=True, help_text='The value of the field before the change', null=True, verbose_name='old value')),
                ('new_value', models.TextField(blank=True, help_text='The value of the field after the change', verbose_name='new value')),
                ('user', models.ForeignKey(help_text='The user who made this change', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='libtektiket_history', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('-when', 'modelname', 'objectid'),
            },
        ),
    ]
