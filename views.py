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
from .forms import TicketForm, TicketTicketNoteForm, TicketTicketNoteFormset
from .models import Technician, History, Ticket, TicketNote
from tougshire_vistas.views import get_vista_object

from libtekin.models import Item, Mmodel


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
        mail_message = mail_message + "\nNotes:\n" + "\n".join([str(note.when) + ': ' + note.text + ' -- ' + str(note.submitted_by) for note in ticket.ticketnote_set.all()])

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
        mail_html_message = mail_html_message + "<br>Notes:<br>\n" + "<br>\n".join([str(note.when) + ': ' + note.text + ' --' + str(note.submitted_by) for note in ticket.ticketnote_set.all()])

    mail_recipients = [
        tech.user.email for tech in Technician.objects.filter(is_current=True).filter(user__isnull=False)
    ]

    if ticket.submitted_by.email is not None:
        mail_recipients.append(ticket.submitted_by.email)

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

        if self.request.POST:
            context_data['ticketnotes'] = TicketTicketNoteFormset(self.request.POST)
        else:
            context_data['ticketnotes'] = TicketTicketNoteFormset()

        return context_data

    def form_valid(self, form):

        response = super().form_valid(form)

        self.object = form.save(commit=False)
        self.object.submitted_by = self.request.user
        self.object.save()

        ticketnotes = TicketTicketNoteFormset(self.request.POST, instance=self.object)

        if(ticketnotes).is_valid():
            for form in ticketnotes.forms:
                if form.has_changed():
                    ticketnote = form.save(commit=False)
                    if ticketnote.submitted_by is None:
                        ticketnote.submitted_by = self.request.user
            ticketnotes.save()
        else:
            for form in ticketnotes.forms:
                print( form.errors )
            return self.form_invalid(form)

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
            context_data['ticketnotes'] = TicketTicketNoteFormset(instance=self.object)

        return context_data


    def form_valid(self, form):

        response = super().form_valid(form)

        self.object = form.save()

        ticketnotes = TicketTicketNoteFormset(self.request.POST, instance=self.object)

        if(ticketnotes).is_valid():

            # for form in ticketnotes.forms:
            #     if form.has_changed():
            #         ticketnote = form.save(commit=False)
            #         if ticketnote.submitted_by is None:
            #             ticketnote.submtted_by = self.request.user

            ticketnotes.save()
        else:
            return self.form_invalid(form)

        if ticketnotes.has_changed():
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
    filter_object = {}
    exclude_object = {}
    order_by = []
    order_by_fields=[]
    combined_text_search=""
    combined_text_fields=[
            'item__common_name',
            'item__mmodel__model_name',
            'item__primary_id',
            'submitted_by__display_name',
            'resolution_notes',
            'short_description',
            'long_description',
    ]

    for fieldname in ['when', 'item', 'urgency']:
        order_by_fields.append(
            { 'name':fieldname, 'label':Ticket._meta.get_field(fieldname).verbose_name.title() }
        )
        order_by_fields.append(
            { 'name':'-' + fieldname, 'label':'{} reverse'.format(Ticket._meta.get_field(fieldname).verbose_name.title()) }
        )
    filter_fields = {
        'in':['item', 'item__mmodel', 'urgency','submitted_by'],
        'exact':['is_resolved'],
        'after':['when']
    }
    # showable_columns = []
    # show_columns = []
    # for fieldname in [
    #         'common_name',
    #         'mmodel',
    #         'primary_id_field',
    #         'serial_number',
    #         'service_number',
    #         'asset_number',
    #         'barcode',
    #         'condition',
    #         'network_name',
    #         'assignee',
    #         'owner',
    #         'borrower',
    #         'home',
    #         'location',
    #         'role',
    #         'latest_inventory'
    #     ]:
    #     showable_columns.append(
    #         {
    #             'name':fieldname,
    #             'label':Ticket._meta.get_field(fieldname).verbose_name.title()
    #         }
    #     )
    #     show_columns.append(fieldname)

    def post(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):

        vista_object = get_vista_object(self, super().get_queryset(), 'libtekticket.ticket' )
        self.filter_object = vista_object['filter_object']
        self.order_by = vista_object['order_by']
        self.show_columns = vista_object['show_columns']
        self.combined_text_search = vista_object['combined_text_search']
        return vista_object['queryset']

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data['mmodels'] = Mmodel.objects.all()
        context_data['urgencies'] = Ticket.URGENCY_CHOICES
        context_data['vistas'] = Vista.objects.filter(user=self.request.user, model_name='libtekticket.ticket').all()
        context_data['order_by_fields'] = self.order_by_fields
        context_data['order_by'] = self.order_by
        # context_data['showable_columns'] = self.showable_columns
        # context_data['show_columns'] = self.show_columns
        context_data['combined_text_search'] = self.combined_text_search
        context_data['ordering'] = Ticket._meta.ordering
        context_data['items'] = Item.objects.all()
        context_data['users'] = get_user_model().objects.all()

        if self.filter_object:
            context_data['filter_object'] = self.filter_object
        if self.request.POST.get('vista__name'):
            context_data['vista__name'] = self.request.POST.get('vista__name')

        context_data['ticket_labels'] = { field.name: field.verbose_name.title() for field in Ticket._meta.get_fields() if type(field).__name__[-3:] != 'Rel' }

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
