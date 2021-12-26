from django.forms import ModelForm, inlineformset_factory, Select
from .models import Ticket, TicketNote

class ItemSelect(Select):
    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super().create_option(name, value, label, selected, index, subindex, attrs)
        if value:
            option['attrs']['data-location'] = value.instance.location.pk
        return option


class TicketForm(ModelForm):
    class Meta:
        model = Ticket
        fields = [
            'item',
            'location',
            'description',
            'urgency',
            'technician',
        ]
        widgets = {
            'item':ItemSelect
        }


class TicketNoteForm(ModelForm):
    class Meta:
        model = TicketNote
        fields = [
            'ticket',
            'when',
            'text',
        ]

TicketTicketNoteFormSet = inlineformset_factory(Ticket, TicketNote, TicketNoteForm, extra=0)
