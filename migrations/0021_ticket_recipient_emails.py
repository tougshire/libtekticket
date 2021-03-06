# Generated by Django 3.2.9 on 2022-02-05 00:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('libtekticket', '0020_alter_ticket_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='ticket',
            name='recipient_emails',
            field=models.TextField(blank=True, help_text='The comma-separated list of emails of those who should get updates on this ticket', verbose_name='recipient emails'),
        ),
    ]
