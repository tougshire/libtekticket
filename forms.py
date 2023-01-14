from django import forms
from django.forms import inlineformset_factory
from .models import Ticket, TicketNote

class ItemSelect(forms.Select):
    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super().create_option(name, value, label, selected, index, subindex, attrs)
        if value:
            textforfilter = f'{name}|{value.instance.primary_id}'
            if value.instance.location is not None:
                option['attrs']['data-home'] = value.instance.home.pk
                textforfilter = textforfilter + f'|{value.instance.home.short_name}|{value.instance.home.full_name}'

            if value.instance.assignee is not None:
                textforfilter = textforfilter + f'|{value.instance.assignee.friendly_name}|{value.instance.assignee.full_name}'
                option['attrs']['data-textforfilter'] = textforfilter

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
            'is_resolved',
            'recipient_emails',
            'resolution_notes',
        ]
        widgets = {
            'item':ItemSelect,
            'short_description':forms.TextInput(attrs={'class':'widthlong'}),
            'long_description':forms.Textarea(attrs={'class':'widthlong'}),
        }


class TicketTicketNoteForm(forms.ModelForm):
    class Meta:
        model = TicketNote
        fields = [
            'when',
            'maintext',
        ]
        widgets={
            'when':forms.DateTimeInput(format='%Y-%m-%dT%H:%M:%S',  attrs={'type':'datetime-local'} ),
            'maintext':forms.TextInput(attrs={'class':'len100'})
        }

TicketTicketNoteFormset = inlineformset_factory(Ticket, TicketNote, form=TicketTicketNoteForm, extra=10)
