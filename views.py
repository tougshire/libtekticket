import json

from django.apps import AppConfig
from django.conf import settings
from django.contrib.auth.mixins import PermissionRequiredMixin, UserPassesTestMixin
from django.core.exceptions import FieldError, ObjectDoesNotExist
from django.core.mail import send_mail
from django.db.models.fields import EmailField
from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.views.generic.list import ListView
from tougshire_vistas.models import Vista
from django.contrib.auth import get_user_model
from .forms import TicketForm, TicketTicketNoteForm
from .models import Technician, History, Ticket, TicketNote

from libtekin.models import Item, Mmodel

def update_history(form, modelname, object, user):
    for fieldname in form.changed_data:
        try:
            old_value=str(form.initial[fieldname]),
        except KeyError:
            old_value=None

        history = History.objects.create(
            user=user,
            modelname=modelname,
            objectid=object.pk,
            fieldname=fieldname,
            old_value=old_value,
            new_value=str(form.cleaned_data[fieldname])
        )

        history.save()

def send_ticket_mail( ticket, request, is_new=False ):
    """Send an email

    Args:
        ticket: The ticket about which the email is being sent.  Usually self.object or self.object.ticket
        request: A request object.  Usually self.request
        is_new: If this mail is about the creation of a new ticket.  If not then it's an update

    """
    ticket_url = request.build_absolute_uri( reverse('libtekticket:ticket-detail', kwargs={'pk':ticket.pk}) )

    mail_subject_action = "Submitted" if is_new else "Updated"
    mail_subject = f"Ticke Ticket { mail_subject_action }: { ticket.short_description }"

    mail_from = settings.LIBTEKTICKET_EMAIL_FROM if hasattr(settings, 'LIBTEKTICKET_FROM_EMAIL') else settings.DEFAULT_FROM_EMAIL

    mail_message = "\r".join(
        [
            f"Urgency: { ticket.get_urgency_display() }",
            f"Item: { ticket.item }",
            f"Description: { ticket.long_description }",
            f"Ticket URL: { ticket_url }"
        ]
    )
    mail_html_message = "<br>".join(
        [
            f"Urgency: { ticket.get_urgency_display() }",
            f"Item: { ticket.item }",
            f"Description: { ticket.long_description }",
            f"Ticket URL: <a href=\"{ ticket_url }\">ticket_url</a>"
        ]
    )
    mail_recipients = [ tech.user.email for tech in Technician.objects.filter(user__isnull=False) ]

    print('tp m15f46 mail recipients')
    print(mail_recipients)

    if  ticket.submitted_by.email is not None:
        mail_recipients.append( ticket.submitted_by.email )

    print('tp m15f47 mail recipients')
    print(mail_recipients)

    send_mail(
        mail_subject,
        mail_message,
        mail_from,
        mail_recipients,
        html_message=mail_html_message,
        fail_silently=False,
    )

class TicketCreate(PermissionRequiredMixin, CreateView):
    permission_required = 'libtekticket.add_ticket'
    model = Ticket
    form_class = TicketForm

    def get_context_data(self, **kwargs):

        context_data = super().get_context_data(**kwargs)

        return context_data

    def form_valid(self, form):

        response = super().form_valid(form)

        self.object = form.save(commit=False)
        self.object.submitted_by = self.request.user

        self.object = form.save()

        send_ticket_mail( self.object, self.request, is_new=True )

        return response

    def get_success_url(self):

        if 'opener' in self.request.POST and self.request.POST['opener'] > '':
            return reverse_lazy('libtekticket:ticket-close', kwargs={'pk': self.object.pk})
        else:
            return reverse_lazy('libtekticket:ticket-detail', kwargs={'pk': self.object.pk})

class TicketUpdate(PermissionRequiredMixin, UpdateView):
    permission_required = 'libtekticket.change_ticket'
    model = Ticket
    form_class = TicketForm

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        return context_data

    def form_valid(self, form):

        update_history(form, 'Item', form.instance, self.request.user)

        response = super().form_valid(form)

        return response

    def get_success_url(self):
        return reverse_lazy('libtekticket:ticket-detail', kwargs={ 'pk':self.object.pk })


class TicketDetail(PermissionRequiredMixin, DetailView):
    permission_required = 'libtekticket.view_ticket'
    model = Ticket

    def get_context_data(self, **kwargs):

        context_data = super().get_context_data(**kwargs)
        context_data['ticket_labels'] = { field.name: field.verbose_name.title() for field in Ticket._meta.get_fields() if type(field).__name__[-3:] != 'Rel' }
        context_data['ticketnote_labels'] = { field.name: field.verbose_name.title() for field in TicketNote._meta.get_fields() if type(field).__name__[-3:] != 'Rel' }
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
        context_data['current_notes'] = self.object.ticketnote_set.all().filter(is_current_status=True)
        context_data['ticket_labels'] = { field.name: field.verbose_name.title() for field in Ticket._meta.get_fields() if type(field).__name__[-3:] != 'Rel' }
        context_data['ticketnote_labels'] = { field.name: field.verbose_name.title() for field in TicketNote._meta.get_fields() if type(field).__name__[-3:] != 'Rel' }

        return context_data

class TicketList(PermissionRequiredMixin, ListView):
    permission_required = 'libtekticket.view_ticket'
    model = Ticket
    filter_object = {}
    exclude_object = {}
    order_by = []
    order_by_fields=[]
    for fieldname in ['item', 'urgency']:
        order_by_fields.append(
            { 'name':fieldname, 'label':Ticket._meta.get_field(fieldname).verbose_name.title() }
        )
        order_by_fields.append(
            { 'name':'-' + fieldname, 'label':'{} reverse'.format(Ticket._meta.get_field(fieldname).verbose_name.title()) }
        )

    def post(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):

        order_by = []
        filter_object={}

        if 'query_submitted' in self.request.POST:

            for i in range(0,3):
                order_by_i = 'order_by_{}'.format(i)
                if order_by_i in self.request.POST:
                    for field in self.order_by_fields:
                        if self.request.POST.get(order_by_i) == field['name']:
                            order_by.append(field['name'])

            for fieldname in ['mmodel', 'mmodel__category', 'condition', 'role']:
                filterfieldname = 'filter__' + fieldname + '__in'
                if filterfieldname in self.request.POST and self.request.POST.get(filterfieldname) > '':
                    postfields = self.request.POST.getlist(filterfieldname)
                    fieldlist = []
                    for postfield in postfields:
                        if postfield.isdecimal():
                            fieldlist.append(postfield)
                    if fieldlist:
                        filter_object[fieldname + '__in'] = postfields

                filterfieldnone = 'filter__' + fieldname + '__none'
                if filterfieldnone in self.request.POST:
                    filter_object[fieldname] = None


            vista__name = ''
            if 'vista__name' in self.request.POST and self.request.POST.get('vista__name') > '':
                vista__name = self.request.POST.get('vista__name')

            if filter_object or order_by:

                queryset = super().get_queryset()

                vista, created = Vista.objects.get_or_create( user=self.request.user, model_name='libtekticket.ticket', name=vista__name )

                if filter_object:
                    self.filter_object = filter_object
                    vista.filterstring = json.dumps( filter_object )
                    queryset = queryset.filter(**filter_object)

                if order_by:
                    self.order_by = order_by
                    vista.sortstring = ','.join(order_by)
                    queryset = queryset.order_by(*order_by)

                vista.save()

                return queryset

        elif 'get_vista' in self.request.POST:

            vista__name = ''

            if 'vista__name' in self.request.POST and self.request.POST.get('vista__name') > '':
                vista__name = self.request.POST.get('vista__name')

            vista, created = Vista.objects.get_or_create( user=self.request.user, model_name='libtekticket.ticket', name=vista__name )

            try:
                filter_object = json.loads(vista.filterstring)
                order_by = vista.sortstring.split(',')
                queryset = super().get_queryset().filter(**filter_object).order_by(*order_by)
                self.filter_object = filter_object

                return queryset

            except json.JSONDecodeError:
                pass

        elif 'delete_vista' in self.request.POST:

            vista__name = ''

            if 'vista__name' in self.request.POST and self.request.POST.get('vista__name') > '':

                vista__name = self.request.POST.get('vista__name')
                Vista.objects.filter( user=self.request.user, model_name='libtekticket.ticket', name=vista__name ).delete()


        # this code runs if no queryset has been returned yet
            vista = Vista.objects.filter( user=self.request.user, is_default=True ).last()
            if vista is None:
                vista = Vista.objects.filter( user=self.request.user ).last()
            if vista is None:
                vista, created = Vista.objects.get_or_create( user=self.request.user )

            try:
                filter_object = json.loads(vista.filterstring)
                order_by = vista.sortstring.split(',')
                try:
                    self.filter_object = filter_object
                    self.order_by = order_by

                    return super().get_queryset().filter(**filter_object).order_by(order_by)

                except (ValueError, TypeError, FieldError):
                    print('Field/Value/Type Error')
                    vista.delete()

            except json.JSONDecodeError:
                print('deserialization error')
                vista.delete()

        return super().get_queryset()

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data['items'] = Item.objects.all()
        context_data['mmodels'] = Mmodel.objects.all()
        context_data['users'] = get_user_model().objects.all()
        context_data['vistas'] = Vista.objects.filter(user=self.request.user, model_name='libtekticket.ticket').all()
        context_data['order_by_fields'] = self.order_by_fields

        for i in range(0,3):
            try:
                context_data['order_by_{}'.format(i)] = self.order_by[i]
            except IndexError:
                pass

        if self.filter_object:
            context_data['filter_object'] = self.filter_object
        if self.request.POST.get('vista__name'):
            context_data['vista__name'] = self.request.POST.get('vista__name')

        context_data['ticket_labels'] = { field.name: field.verbose_name.title() for field in Ticket._meta.get_fields() if type(field).__name__[-3:] != 'Rel' }

        return context_data

class TicketTicketNoteCreate(UserPassesTestMixin, PermissionRequiredMixin, CreateView):
    permission_required = 'libtekticket.add_ticket'
    model = TicketNote
    form_class = TicketTicketNoteForm
    template_name = 'libtekticket/ticketticketnote_form.html'

    def test_func(self):
        try:
            ticket = Ticket.objects.get(pk=self.kwargs.get('ticketpk'))
        except LookupError:
            return False

        return ticket.user_is_editor(self.request.user)

    def get_context_data(self, **kwargs):

        context_data = super().get_context_data(**kwargs)

        context_data['ticket'] = Ticket.objects.get(pk=self.kwargs.get('ticketpk'))

        return context_data

    def form_valid(self, form):


        ticket = Ticket.objects.get(pk=self.kwargs.get('ticketpk'))

        self.object = form.save(commit=False)
        self.object.ticket = ticket
        self.object = form.save()

        response = super().form_valid(form)

        ticket_url = self.request.build_absolute_uri( reverse('libtekticket:ticket-detail', kwargs={'pk':self.object.ticket.pk}) )
        mail_message = "\r".join(
            [
                f"Update to { self.object.ticket }: {self.object.text }"
                f"Item: { self.object.ticket.item }",
                f"Ticket Urgency: {self.object.ticket.get_urgency_display}",
                f"Description: { self.object.ticket.long_description }",
                f"Ticket URL: { ticket_url }"
            ]
        )
        mail_html_message = "<br>".join(
            [
                f"Update to { self.object.ticket }: {self.object.text }"
                f"Item: { self.object.ticket.item }",
                f"Ticket Urgency: {self.object.ticket.get_urgency_display}",
                f"Ticket Description: { self.object.ticket.long_description }",
                f"Ticket URL: <a href=\"{ ticket_url }\">ticket_url</a>"
            ]
        )

        mail_recipients = [
            tech.user.email for tech in Technician.objects.filter(user__isnull=False).filter(user__email__gt='')
        ] + ( [ self.object.submitted_by.email ] if self.object.submitted_by is not None and self.object.submitted_by.email > '' else [] )

        send_mail(
            'Note added to Tech Ticket: ' + self.object.ticket.short_description,
            mail_message,
            'suvapuli@tougshrire.com',
            mail_recipients,
            html_message=mail_html_message,
            fail_silently=False,
        )

        return response

    def get_success_url(self):

        ticket = Ticket.objects.get(pk=self.kwargs.get('ticketpk'))

        if 'opener' in self.request.POST and self.request.POST['opener'] > '':
            return reverse_lazy('libtekticket:ticket-ticketnote-close', kwargs={'pk': self.object.pk})
        else:
            return reverse_lazy('libtekticket:ticket-detail', kwargs={'pk': ticket.pk})

class TicketTicketNoteClose(PermissionRequiredMixin, DetailView):
    permission_required = 'libtekticket.add_ticket'
    model = TicketNote
    template_name = 'libtekticket/ticketticketnote_closer.html'
