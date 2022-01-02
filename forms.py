from django import forms
from .models import Ticket, TicketNote

class ItemSelect(forms.Select):
    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super().create_option(name, value, label, selected, index, subindex, attrs)
        if value:
            option['attrs']['data-location'] = value.instance.location.pk
        return option


class TicketForm(forms.ModelForm):
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
            'short_description':forms.TextInput(attrs={'style':'width:60%'})
        }


class TicketNoteForm(forms.ModelForm):
    class Meta:
        model = TicketNote
        fields = [
            'when',
            'text',
        ]
        widgets={
            'when':forms.DateInput(attrs={'type':'date'}),
            'text':forms.TextInput(attrs={'style':'width:100%'})
        }

TicketTicketNoteFormSet = forms.inlineformset_factory(Ticket, TicketNote, TicketNoteForm, extra=0)
