from django.db import models
from django.conf import settings
from datetime import date
from django.apps import apps
from libtekin.models import Item, Location
from django.contrib.auth import get_user_model
import datetime

class Technician(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name='user',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        help_text='The user account associated with this technician'
    )
    name = models.CharField(
        'name',
        max_length=50,
        blank=True,
        help_text='The name of the technician'
    )
    is_current = models.BooleanField(
        'current',
        default=True,
        help_text='If this technician is current (should receive emails from tickets, etc)'
    )

    def __str__(self):
        return f"{self.name}"

    @classmethod
    def user_is_tech(cls, user):
        return user in [ technician.user for technician in Technician.objects.all() ]

class Ticket(models.Model):
    URGENCY_CHOICES = (
            (1, '1) Safety Hazard or Work Stoppage'),
            (2, '2) Major Work Impediment'),
            (3, '3) Highly Important Issue'),
            (4, '4) Moderately Important Issue'),
            (5, '5) Minor Issue or Suggestion')
    )
    item = models.ForeignKey(
        Item,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text='The item to which this ticket applies - leave blank if not applicable you have trouble finding it'
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text='The location leave blank if not applicable or you have trouble finding it'
    )
    short_description = models.CharField(
        'Short Description',
        max_length=75,
        help_text='A short description of the issue',
    )
    long_description = models.TextField(
        'Description',
        blank=True,
        help_text='The description of the problem if the short description isn\'t adequate'
    )
    urgency = models.IntegerField(
        'Urgency',
        choices=URGENCY_CHOICES,
        help_text='The urgency, on a scale of 1 to 5, where 1 is the most urgent'
    )
    submitted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name='submitted by',
        null=True,
        on_delete=models.SET_NULL,
        help_text='The user who submitted this ticket'
    )
    when = models.DateTimeField(
        default=datetime.date.today,
        help_text='The date and time the ticket was submitted'
    )
    technician = models.ForeignKey(
        Technician,
        verbose_name='technician',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        help_text='The technician responsible for responding to this ticket'
    )
    is_resolved = models.BooleanField(
        'is resolved',
        blank=True,
        default=False,
        help_text = 'If the problem is resolved'

    )
    resolution_notes = models.TextField(
        'resolution notes',
        blank=True,
        help_text='How the problem was resolved'
    )

    def __str__(self):
        return self.short_description

    def user_is_editor(self, user):
        return user == self.submitted_by or user.has_perm('libtekticket.change_ticket')

    class Meta:
        ordering=['-when', 'urgency']


class TicketNote(models.Model):

    ticket=models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE,
        help_text='The ticket to which this note applies',
    )
    text = models.CharField(
        'text',
        max_length=255,
        help_text='The text of the note'
    )
    submitted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name='submitted by',
        null=True,
        on_delete=models.SET_NULL,
        help_text='The user who submitted this note'
    )
    when = models.DateField(
        'when',
        default=date.today,
        help_text='The effective date of the note (when it applies as opposed to when it was actually made)'
    )

    def __str__(self):
        return self.text

class History(models.Model):

    when = models.DateTimeField(
        'when',
        auto_now_add=True,
        help_text='The date this change was made'
    )
    modelname = models.CharField(
        'model',
        max_length=50,
        help_text='The model to which this change applies'
    )
    objectid = models.BigIntegerField(
        'object id',
        null=True,
        blank=True,
        help_text='The id of the record that was changed'
    )
    fieldname = models.CharField(
        'field',
        max_length=50,
        help_text='The that was changed',
    )
    old_value = models.TextField(
        'old value',
        blank=True,
        null=True,
        help_text='The value of the field before the change'
    )
    new_value = models.TextField(
        'new value',
        blank=True,
        help_text='The value of the field after the change'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='libtektiket_history',
        null=True,
        help_text='The user who made this change'
    )

    class Meta:
        ordering = ('-when', 'modelname', 'objectid')

    def __str__(self):

        new_value_trunc = self.new_value[:17:]+'...' if len(self.new_value) > 20 else self.new_value

        try:
            model = apps.get_model('libtekticket', self.modelname)
            object = model.objects.get(pk=self.objectid)
            return f'{self.when.strftime("%Y-%m-%d")}: {self.modelname}: [{object}] [{self.fieldname}] changed to "{new_value_trunc}"'

        except Exception as e:
            print (e)

        return f'{"mdy".format(self.when.strftime("%Y-%m-%d"))}: {self.modelname}: {self.objectid} [{self.fieldname}] changed to "{new_value_trunc}"'


