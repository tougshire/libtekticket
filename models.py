from django.db import models
from django.conf import settings
from datetime import date
from django.apps import apps

class Technician(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name='user',
        null=True,
        on_delete=models.SET_NULL,
        help_text='The user account associated with this technician'
    )
    name = models.CharField(
        'name',
        max_length=50,
        blank=True,
        help_text='The name of the technician'
    )

class Ticket(models.Model):
    item = models.ForeignKey(
        settings.LIBTEKTICKET_ITEM,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text='The item to which this ticket applies'
    )
    description = models.TextField(
        'Description',
        blank=True,
        help_text='The description of the problem'
    )
    urgency = models.IntegerField(
        'Urgency',
        choices=(
             (1, 'Safety Hazard or Work Stoppage'),
            (2, ''),
            (3, 'Important Issue'),
            (4, ''),
            (5, 'Minor Issue or Suggestion')
        ),
        help_text='The urgency, on a scale of 1 to 5, where 1 is the most urgent'
    )
    submitted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name='submitted by',
        null=True,
        on_delete=models.SET_NULL,
        help_text='The user who submitted this ticket'
    )
    technician = models.ForeignKey(
        Technician,
        verbose_name='technician',
        null=True,
        on_delete=models.SET_NULL,
        help_text='The technician responsible for responding to this ticket'
    )
class TicketNote(models.Model):
    ticket=models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE,
        help_text='The ticket to which this note applies',
    ),
    text = models.TextField(
        'text',
        help_text='The text of the note'
    )
    when = models.DateField(
        'when',
        default=date.today,
        help_text='The effective date of the note (when it applies as opposed to when it was actually made)'
    )

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
            model = apps.get_model('libtekin', self.modelname)
            object = model.objects.get(pk=self.objectid)
            return f'{self.when.strftime("%Y-%m-%d")}: {self.modelname}: [{object}] [{self.fieldname}] changed to "{new_value_trunc}"'

        except Exception as e:
            print (e)

        return f'{"mdy".format(self.when.strftime("%Y-%m-%d"))}: {self.modelname}: {self.objectid} [{self.fieldname}] changed to "{new_value_trunc}"'


