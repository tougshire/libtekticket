# Generated by Django 3.2.9 on 2022-01-02 14:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('libtekticket', '0010_auto_20220102_0839'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ticket',
            name='description',
        ),
        migrations.AddField(
            model_name='ticket',
            name='long_description',
            field=models.TextField(blank=True, help_text="The description of the problem if the short description isn't adequate", verbose_name='Description'),
        ),
    ]
