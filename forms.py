from django.forms import ModelForm, inlineformset_factory, Select
from .models import Ticket, TicketNote


class TicketForm(ModelForm):
    class Meta:
        model = Ticket
        fields = [
            'item',
            'description',
            'urgency',
            'technician',
        ]

class TicketNoteForm(ModelForm):
    class Meta:
        model = TicketNote
        fields = [
            'item',
            'when',
            'text',
        ]

TicketTicketNoteFormSet = inlineformset_factory(Ticket, TicketNote, TicketNoteForm, extra=0)
