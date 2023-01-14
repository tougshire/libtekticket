import sys
import urllib
from urllib.parse import urlencode

from django.apps import AppConfig
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import (PermissionRequiredMixin,
                                        UserPassesTestMixin)
from django.core.exceptions import FieldError, ObjectDoesNotExist
from django.core.mail import send_mail
from django.http import QueryDict
from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.views.generic.list import ListView
from libtekin.models import Item, Location, Mmodel
from tougshire_vistas.models import Vista
from tougshire_vistas.views import (delete_vista, get_global_vista,
                                    get_latest_vista, make_vista,
                                    retrieve_vista, default_vista, vista_context_data, make_vista_fields)

from .forms import TicketForm, TicketTicketNoteForm, TicketTicketNoteFormset
from .models import History, Technician, Ticket, TicketNote


def update_history(form, modelname, object, user):
    for fieldname in form.changed_data:
        try:
            old_value = str(form.initial[fieldname]),
        except KeyError:
            old_value = None

        history = History.objects.create(
            user=user,
            modelname=modelname,
            objectid=object.pk,
            fieldname=fieldname,
            old_value=old_value,
            new_value=str(form.cleaned_data[fieldname])
        )

        history.save()


def send_ticket_mail(ticket, request, is_new=False):
    """Send an email

    Args:
        ticket: The ticket about which the email is being sent.  Usually self.object or self.object.ticket
        request: A request object.  Usually self.request
        is_new: If this mail is about the creation of a new ticket.  If not then it's an update

    """

    # if it has no @ sign, assume no emails should be sent
    if not ticket.recipient_emails.find('@') > 0:
        return

    ticket_url = request.build_absolute_uri(
        reverse('libtekticket:ticket-detail', kwargs={'pk': ticket.pk}))

    mail_subject_action = "Submitted" if is_new else "Updated"
    mail_subject = f"Tech Ticket { mail_subject_action }: { ticket.short_description }"

    mail_from = settings.LIBTEKTICKET_EMAIL_FROM if hasattr(
        settings, 'LIBTEKTICKET_FROM_EMAIL') else settings.DEFAULT_FROM_EMAIL

    mail_message = "\n".join(
        [
            f"Title: { ticket.short_description }",
            f"Urgency: { ticket.get_urgency_display() }",
            f"Item: { ticket.item }",
            f"Description: { ticket.long_description }",
            f"Ticket URL: { ticket_url }",
        ]
    )
    if ticket.ticketnote_set.all().exists:
        mail_message = mail_message + "\nNotes:\n" + "\n".join([str(note.when) + ': ' + note.maintext + ' -- ' + str(note.submitted_by) for note in ticket.ticketnote_set.all()])

    mail_html_message = "<br>\n".join(
        [
            f"Title: { ticket.short_description }",
            f"Urgency: { ticket.get_urgency_display() }",
            f"Item: { ticket.item }",
            f"Description: { ticket.long_description }",
            f"Ticket URL: <a href=\"{ ticket_url }\">{ ticket_url }</a>"
        ]
    )
    if ticket.ticketnote_set.all().exists:
        mail_html_message = mail_html_message + "<br>Notes:<br>\n" + "<br>\n".join([str(note.when) + ': ' + note.maintext + ' --' + str(note.submitted_by) for note in ticket.ticketnote_set.all()])


    mail_recipients = [email.strip() for email in ticket.recipient_emails.split(',')]

    try:
        send_mail(
            mail_subject,
            mail_message,
            mail_from,
            mail_recipients,
            html_message=mail_html_message,
            fail_silently=False,
        )
    except Exception as e:
        messages.add_message(request, messages.WARNING, 'There was an error sending emails.')
        messages.add_message(request, messages.WARNING, e)

        print(e, ' at ', sys.exc_info()[2].tb_lineno)

class TicketCreate(PermissionRequiredMixin, CreateView):
    permission_required = 'libtekticket.add_ticket'
    model = Ticket
    form_class = TicketForm

    def get_context_data(self, **kwargs):

        context_data = super().get_context_data(**kwargs)

        if self.request.POST:
            context_data['ticketnotes'] = TicketTicketNoteFormset(self.request.POST)
        else:
            context_data['ticketnotes'] = TicketTicketNoteFormset(initial=[
            {
                'submitted_by': self.request.user
            }
        ])


        return context_data

    def get_initial(self):
        tech_emails = [tech.user.email for tech in Technician.objects.filter(is_current=True).filter(user__isnull=False)]
        all_recipient_emails = ( tech_emails + [ self.request.user.email ] ) if self.request.user.email not in tech_emails else tech_emails
        return {
            'recipient_emails': ",\n".join(all_recipient_emails)
        }

    def form_valid(self, form):

        response = super().form_valid(form)

        self.object = form.save(commit=False)
        self.object.submitted_by = self.request.user
        if not 'recipient_emails' in self.request.POST:
            self.object.recipient_emails = self.get_initial()['recipient_emails']

        self.object.save()

        ticketnotes = TicketTicketNoteFormset(self.request.POST, instance=self.object)

        if(ticketnotes).is_valid():
            for form in ticketnotes.forms:
                ticketnote = form.save(commit=False)
                if ticketnote.submitted_by is None:
                    ticketnote.submitted_by = self.request.user
            ticketnotes.save()
        else:
            return self.form_invalid(form)


        if not 'donot_send' in self.request.POST:
            send_ticket_mail(self.object, self.request, is_new=True)

        return response

    def get_success_url(self):
        return reverse_lazy('libtekticket:ticket-detail', kwargs={'pk': self.object.pk})


class TicketUpdate(PermissionRequiredMixin, UpdateView):
    permission_required = 'libtekticket.change_ticket'

    model = Ticket
    form_class = TicketForm

    def get_context_data(self, **kwargs):

        context_data = super().get_context_data(**kwargs)

        if self.request.POST:
            context_data['ticketnotes'] = TicketTicketNoteFormset(self.request.POST, instance=self.object)
        else:
            context_data['ticketnotes'] = TicketTicketNoteFormset(instance=self.object, initial=[{'submitted_by':self.request.user}])

        return context_data


    def form_valid(self, form):

        response = super().form_valid(form)

        self.object = form.save()

        ticketnotes = TicketTicketNoteFormset(self.request.POST, instance=self.object, initial=[
            {
                'submitted_by': self.request.user
            }
        ])

        if(ticketnotes).is_valid():
            for form in ticketnotes.forms:
                ticketnote = form.save(commit=False)
                if ticketnote.submitted_by is None:
                    ticketnote.submitted_by = self.request.user
            ticketnotes.save()
        else:
            return self.form_invalid(form)

        if not 'donot_send' in self.request.POST:
            send_ticket_mail(self.object, self.request, is_new=False)

        return response

    def get_success_url(self):

        return reverse_lazy('libtekticket:ticket-detail', kwargs={'pk': self.object.pk})

class TicketDetail(PermissionRequiredMixin, DetailView):
    permission_required = 'libtekticket.view_ticket'
    model = Ticket

    def get_context_data(self, **kwargs):

        context_data = super().get_context_data(**kwargs)
        context_data['ticket_labels'] = {field.name: field.verbose_name.title(
        ) for field in Ticket._meta.get_fields() if type(field).__name__[-3:] != 'Rel'}
        context_data['ticketnote_labels'] = {field.name: field.verbose_name.title(
        ) for field in TicketNote._meta.get_fields() if type(field).__name__[-3:] != 'Rel'}
        return context_data


class TicketDelete(PermissionRequiredMixin, UpdateView):
    permission_required = 'libtekticket.delete_ticket'
    model = Ticket
    success_url = reverse_lazy('libtekticket:ticket-list')


class TicketSoftDelete(PermissionRequiredMixin, UpdateView):
    permission_required = 'libtekticket.delete_ticket'
    model = Ticket
    template_name = 'libtekticket/item_confirm_delete.html'
    success_url = reverse_lazy('libtekticket:ticket-list')
    fields = ['is_deleted']

    def get_context_data(self, **kwargs):

        context_data = super().get_context_data(**kwargs)
        context_data['current_notes'] = self.object.ticketnote_set.all().filter(
            is_current_status=True)
        context_data['ticket_labels'] = {field.name: field.verbose_name.title(
        ) for field in Ticket._meta.get_fields() if type(field).__name__[-3:] != 'Rel'}
        context_data['ticketnote_labels'] = {field.name: field.verbose_name.title(
        ) for field in TicketNote._meta.get_fields() if type(field).__name__[-3:] != 'Rel'}

        return context_data

class TicketList(PermissionRequiredMixin, ListView):
    permission_required = 'libtekticket.view_ticket'
    model = Ticket
    paginate_by = 30

    def setup(self, request, *args, **kwargs):
        self.vista_settings={
            'max_search_keys':10,
            'fields':[],
        }

        self.vista_settings['fields'] = make_vista_fields(Ticket, rels=True)

        self.vista_defaults = QueryDict(urlencode([
            ('filter__fieldname', ['is_resolved']),
            ('filter__op', ['exact']),
            ('filter__value', [False]),
            ('order_by', ['priority', 'begin']),
            ('paginate_by',self.paginate_by),
        ],doseq=True) )

        return super().setup(request, *args, **kwargs)


    def post(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):

        queryset = super().get_queryset()

        self.vistaobj = {'querydict':QueryDict(), 'queryset':queryset}

        if 'delete_vista' in self.request.POST:
            delete_vista(self.request)

        if 'query' in self.request.session:
            querydict = QueryDict(self.request.session.get('query'))
            self.vistaobj = make_vista(
                self.request.user,
                queryset,
                querydict,
                '',
                False,
                self.vista_settings
            )
            del self.request.session['query']

        elif 'vista_query_submitted' in self.request.POST:

            self.vistaobj = make_vista(
                self.request.user,
                queryset,
                self.request.POST,
                self.request.POST.get('vista_name') if 'vista_name' in self.request.POST else '',
                self.request.POST.get('make_default') if ('make_default') in self.request.POST else False,
                self.vista_settings
            )
        elif 'retrieve_vista' in self.request.POST:
            self.vistaobj = retrieve_vista(
                self.request.user,
                queryset,
                'libtekin.item',
                self.request.POST.get('vista_name'),
                self.vista_settings

            )
        else:
            self.vistaobj = default_vista(
                self.request.user,
                queryset,
                self.vista_defaults,
                self.vista_settings
            )

        return self.vistaobj['queryset']

    def get_paginate_by(self, queryset):

        if 'paginate_by' in self.vistaobj['querydict'] and self.vistaobj['querydict']['paginate_by']:
            return self.vistaobj['querydict']['paginate_by']

        return super().get_paginate_by(self)

    def get_context_data(self, **kwargs):

        context_data = super().get_context_data(**kwargs)

        vista_data = vista_context_data(self.vista_settings, self.vistaobj['querydict'])
        context_data = {**context_data, **vista_data}

        context_data['vistas'] = Vista.objects.filter(user=self.request.user, model_name='libtekin.ticket').all() # for choosing saved vistas

        if self.request.POST.get('vista_name'):
            context_data['vista_name'] = self.request.POST.get('vista_name')

        return context_data

class TicketTicketNoteCreate(PermissionRequiredMixin, CreateView):
    permission_required = 'libtekticket.add_ticketnote'
    model=TicketNote
    form_class=TicketTicketNoteForm
    template_name='libtekticket/ticketticketnote_form.html'

    def form_valid(self, form):

        self.object=form.save(commit=False)
        self.object.ticket=Ticket.objects.get(pk=self.kwargs.get('ticketpk'))
        self.object.submitted_by = self.request.user
        self.object.save()

        send_ticket_mail(self.object.ticket, self.request, is_new=False)

        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('libtekticket:ticket-detail', kwargs={'pk': self.object.ticket.pk})
