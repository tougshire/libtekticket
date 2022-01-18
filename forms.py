from django import forms
from django.forms import inlineformset_factory
from .models import Ticket, TicketNote

class ItemSelect(forms.Select):
    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super().create_option(name, value, label, selected, index, subindex, attrs)
        if value:
            if value.instance.location is not None:
                option['attrs']['data-location'] = value.instance.location.pk
        return option


class TicketForm(forms.ModelForm):
    def __init__(self, **kwargs):
        return super().__init__(**kwargs)

    class Meta:
        model = Ticket
        fields = [
            'item',
            'location',
            'short_description',
            'long_description',
            'urgency',
            'technician',
        ]
        widgets = {
            'item':ItemSelect,
            'short_description':forms.TextInput(attrs={'class':'len75'}),
            'long_description':forms.Textarea(attrs={'class':'len75'}),
        }


class TicketNoteForm(forms.ModelForm):
    class Meta:
        model = TicketNote
        fields = [
            'ticket',
            'when',
            'text',
        ]
        widgets={
            'when':forms.DateInput(attrs={'type':'date'}),
            'text':forms.TextInput(attrs={'class':'len100'})
        }

TicketTicketNoteFormset = inlineformset_factory(Ticket, TicketNote, form=TicketNoteForm, extra=10)
