from django import forms
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
        print('tp m16830')
        print(getattr(self._meta, 'fields'))
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


class TicketTicketNoteForm(forms.ModelForm):
    class Meta:
        model = TicketNote
        fields = [
            'when',
            'text',
        ]
        widgets={
            'when':forms.DateInput(attrs={'type':'date'}),
            'text':forms.TextInput(attrs={'class':'len100'})
        }

#TicketTicketNoteFormSet = forms.inlineformset_factory(Ticket, TicketNote, TicketNoteForm, extra=0)
