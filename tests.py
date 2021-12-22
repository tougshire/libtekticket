from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.views.generic.list import ListView
from django.core.exceptions import FieldError, ObjectDoesNotExist
from .forms import EntityForm, ItemForm, ticketnoteForm, ItemticketnoteFormSet, LocationForm, MmodelForm, MmodelCategoryForm
from .models import Condition, Entity, Item, ticketnote, Location, Mmodel, MmodelCategory, Role, ViewItem, History

class TicketCreate(PermissionRequiredMixin, CreateView):
    permission_required = 'libtekin.add_ticket'
    model = Ticket
    form_class = TicketForm

    def get_context_data(self, **kwargs):

        context_data = super().get_context_data(**kwargs)

        if self.request.POST:
            context_data['ticketnotes'] = TicketTicketnoteFormSet(self.request.POST)
        else:
            context_data['ticketnotes'] = TicketTicketnoteFormSet()

        return context_data

    def form_valid(self, form):

        response = super().form_valid(form)

        update_history(form, 'Item', form.instance, self.request.user)

        self.object = form.save()

        ticketnotes = ItemticketnoteFormSet(self.request.POST, instance=self.object)

        if ticketnotes.is_valid():
            for form in ticketnotes.forms:
                update_history(form, 'ticketnote', form.instance, self.request.user)

            ticketnotes.save()
        else:
            print("formset is not not valid")
            print(ticketnotes.errors)
            for form in ticketnotes.forms:
                print( form.errors )

        return response

    def get_success_url(self):
        if 'opener' in self.request.POST and self.request.POST['opener'] > '':
            return reverse_lazy('libtekin:item-close', kwargs={'pk': self.object.pk})
        else:
            return reverse_lazy('libtekin:item-detail', kwargs={'pk': self.object.pk})



class TicketUpdate(PermissionRequiredMixin, UpdateView):
    permission_required = 'libtekin.change_ticket'
    model = Ticket
    form_class = TicketForm

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        if self.request.POST:
            context_data['ticketnotes'] = ItemticketnoteFormSet(self.request.POST, instance=self.object)
        else:
            context_data['ticketnotes'] = ItemticketnoteFormSet(instance=self.object)

        return context_data

    def form_valid(self, form):

        if 'copy' in self.request.POST:
            form.instance.pk=None

        update_history(form, 'Item', form.instance, self.request.user)

        response = super().form_valid(form)

        ticketnotes = ItemticketnoteFormSet(self.request.POST, instance=self.object)

        if ticketnotes.is_valid():

            for form in ticketnotes.forms:
                update_history(form, 'Item', form.instance, self.request.user)

            ticketnotes.save()
        else:
            print("formset is not not valid")
            print(ticketnotes.errors)
            for form in ticketnotes.forms:
                print( form.errors )

        return response

    def get_success_url(self):
        return reverse_lazy('libtekin:item-detail', kwargs={ 'pk':self.object.pk })


class TicketDetail(PermissionRequiredMixin, DetailView):
    permission_required = 'libtekin.view_ticket'
    model = Ticket

    def get_context_data(self, **kwargs):

        context_data = super().get_context_data(**kwargs)
        context_data['item_labels'] = { field.name: field.verbose_name.title() for field in Item._meta.get_fields() if type(field).__name__[-3:] != 'Rel' }
        context_data['ticketnote_labels'] = { field.name: field.verbose_name.title() for field in ticketnote._meta.get_fields() if type(field).__name__[-3:] != 'Rel' }

        return context_data

class TicketDelete(PermissionRequiredMixin, UpdateView):
    permission_required = 'libtekin.delete_ticket'
    model = Ticket
    success_url = reverse_lazy('libtekin:item-list')

class TicketSoftDelete(PermissionRequiredMixin, UpdateView):
    permission_required = 'libtekin.delete_ticket'
    model = Ticket
    template_name = 'libtekin/item_confirm_delete.html'
    success_url = reverse_lazy('libtekin:item-list')
    fields = ['is_deleted']

    def get_context_data(self, **kwargs):

        context_data = super().get_context_data(**kwargs)
        context_data['current_notes'] = self.object.ticketnote_set.all().filter(is_current_status=True)
        context_data['item_labels'] = { field.name: field.verbose_name.title() for field in Item._meta.get_fields() if type(field).__name__[-3:] != 'Rel' }
        context_data['ticketnote_labels'] = { field.name: field.verbose_name.title() for field in ticketnote._meta.get_fields() if type(field).__name__[-3:] != 'Rel' }

        return context_data

class TicketList(PermissionRequiredMixin, ListView):
    permission_required = 'libtekin.view_ticket'
    model = Ticket
    filter_object = {}
    exclude_object = {}
    order_by = []
    order_by_fields=[]
    for fieldname in ['common_name', 'mmodel', 'primary_id', 'serial_number','service_number']:
        order_by_fields.append(
            { 'name':fieldname, 'label':Item._meta.get_field(fieldname).verbose_name.title() }
        )
        order_by_fields.append(
            { 'name':'-' + fieldname, 'label':'{} reverse'.format(Item._meta.get_field(fieldname).verbose_name.title()) }
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


            viewitem__name = ''
            if 'viewitem__name' in self.request.POST and self.request.POST.get('viewitem__name') > '':
                viewitem__name = self.request.POST.get('viewitem__name')

            if filter_object or order_by:

                queryset = super().get_queryset()

                viewitem, created = ViewItem.objects.get_or_create( user=self.request.user, name=viewitem__name )

                if filter_object:
                    self.filter_object = filter_object
                    viewitem.filterstring = json.dumps( filter_object )
                    queryset = queryset.filter(**filter_object)

                if order_by:
                    self.order_by = order_by
                    viewitem.sortstring = ','.join(order_by)
                    queryset = queryset.order_by(*order_by)

                viewitem.save()

                return queryset

        elif 'get_viewitem' in self.request.POST:

            viewitem__name = ''

            if 'viewitem__name' in self.request.POST and self.request.POST.get('viewitem__name') > '':
                viewitem__name = self.request.POST.get('viewitem__name')

            viewitem, created = ViewItem.objects.get_or_create( user=self.request.user, name=viewitem__name )

            try:
                filter_object = json.loads(viewitem.filterstring)
                order_by = viewitem.sortstring.split(',')
                queryset = super().get_queryset().filter(**filter_object).order_by(*order_by)
                self.filter_object = filter_object

                return queryset

            except json.JSONDecodeError:
                pass

        elif 'delete_viewitem' in self.request.POST:

            viewitem__name = ''

            if 'viewitem__name' in self.request.POST and self.request.POST.get('viewitem__name') > '':

                viewitem__name = self.request.POST.get('viewitem__name')
                ViewItem.objects.filter( user=self.request.user, name=viewitem__name ).delete()


        # this code runs if no queryset has been returned yet
            viewitem = ViewItem.objects.filter( user=self.request.user, is_default=True ).last()
            if viewitem is None:
                viewitem = ViewItem.objects.filter( user=self.request.user ).last()
            if viewitem is None:
                viewitem, created = ViewItem.objects.get_or_create( user=self.request.user )

            try:
                filter_object = json.loads(viewitem.filterstring)
                order_by = viewitem.sortstring.split(',')
                try:
                    self.filter_object = filter_object
                    self.order_by = order_by

                    return super().get_queryset().filter(**filter_object).order_by(order_by)

                except (ValueError, TypeError, FieldError):
                    print('Field/Value/Type Error')
                    viewitem.delete()

            except json.JSONDecodeError:
                print('deserialization error')
                viewitem.delete()

        return super().get_queryset()

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data['mmodels'] = Mmodel.objects.all()
        context_data['mmodelcategories'] = MmodelCategory.objects.all()
        context_data['conditions'] = Condition.objects.all()
        context_data['roles'] = Role.objects.all()
        context_data['viewitems'] = ViewItem.objects.filter(user=self.request.user).all()
        context_data['order_by_fields'] = self.order_by_fields

        for i in range(0,3):
            try:
                context_data['order_by_{}'.format(i)] = self.order_by[i]
            except IndexError:
                pass

        if self.filter_object:
            context_data['filter_object'] = self.filter_object
        if self.request.POST.get('viewitem__name'):
            context_data['viewitem__name'] = self.request.POST.get('viewitem__name')

        context_data['item_labels'] = { field.name: field.verbose_name.title() for field in Item._meta.get_fields() if type(field).__name__[-3:] != 'Rel' }

        return context_data

class TicketClose(PermissionRequiredMixin, DetailView):
    permission_required = 'libtekin.view_ticket'
    model = Ticket
    template_name = 'libtekin/item_closer.html'

class MmodelCreate(PermissionRequiredMixin, CreateView):
    permission_required = 'libtekin.add_mmodel'
    model = Mmodel
    form_class = MmodelForm

    def get_success_url(self):
        if 'opener' in self.request.POST and self.request.POST['opener'] > '':
            return reverse_lazy('libtekin:mmodel-close', kwargs={'pk': self.object.pk})
        else:
            return reverse_lazy('libtekin:mmodel-detail', kwargs={'pk': self.object.pk})

        return response

class MmodelUpdate(PermissionRequiredMixin, UpdateView):
    permission_required = 'libtekin.change_mmodel'
    model = Mmodel
    form_class = MmodelForm

    def get_success_url(self):
        return reverse_lazy('libtekin:mmodel-detail', kwargs={'pk': self.object.pk})


class MmodelDetail(PermissionRequiredMixin, DetailView):
    permission_required = 'libtekin.view_mmodel'
    model = Mmodel

    def get_context_data(self, **kwargs):

        context_data = super().get_context_data(**kwargs)
        context_data['mmodel_labels'] = { field.name: field.verbose_name.title() for field in Mmodel._meta.get_fields() if type(field).__name__[-3:] != 'Rel' }

        return context_data


class MmodelDelete(PermissionRequiredMixin, DeleteView):
    permission_required = 'libtekin.delete_mmodel'
    model = Mmodel
    success_url = reverse_lazy('libtekin:mmodel-list')

class MmodelList(PermissionRequiredMixin, ListView):
    permission_required = 'libtekin.view_mmodel'
    model = Mmodel

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data['mmodel_labels'] = { field.name: field.verbose_name.title() for field in Mmodel._meta.get_fields() if type(field).__name__[-3:] != 'Rel' }
        return context_data

class MmodelClose(PermissionRequiredMixin, DetailView):
    permission_required = 'libtekin.view_mmodel'
    model = Mmodel
    template_name = 'libtekin/mmodel_closer.html'

class MmodelCategoryCreate(PermissionRequiredMixin, CreateView):
    permission_required = 'libtekin.add_MmodelCategory'
    model = MmodelCategory
    form_class = MmodelCategoryForm

    def get_success_url(self):
        if 'opener' in self.request.POST and self.request.POST['opener'] > '':
            return reverse_lazy('libtekin:mmodelcategory-close', kwargs={'pk': self.object.pk})
        else:
            return reverse_lazy('libtekin:mmodelcategory-detail', kwargs={'pk': self.object.pk})

        return response

class MmodelCategoryUpdate(PermissionRequiredMixin, UpdateView):
    permission_required = 'libtekin.change_MmodelCategory'
    model = MmodelCategory
    form_class = MmodelCategoryForm

    def get_success_url(self):
        return reverse_lazy('libtekin:mmodelcategory-detail', kwargs={'pk': self.object.pk})

class MmodelCategoryDetail(PermissionRequiredMixin, DetailView):
    permission_required = 'libtekin.view_MmodelCategory'
    model = MmodelCategory

class MmodelCategoryDelete(PermissionRequiredMixin, DeleteView):
    permission_required = 'libtekin.delete_MmodelCategory'
    model = MmodelCategory
    success_url = reverse_lazy('libtekin:MmodelCategory-list')

class MmodelCategoryList(PermissionRequiredMixin, ListView):
    permission_required = 'libtekin.view_MmodelCategory'
    model = MmodelCategory

class MmodelCategoryClose(PermissionRequiredMixin, DetailView):
    permission_required = 'libtekin.view_MmodelCategory'
    model = MmodelCategory
    template_name = 'libtekin/MmodelCategory_closer.html'

class LocationCreate(PermissionRequiredMixin, CreateView):
    permission_required = 'libtekin.add_location'
    model = Location
    form_class = LocationForm

    def get_success_url(self):
        if 'opener' in self.request.POST and self.request.POST['opener'] > '':
            return reverse_lazy('libtekin:location-close', kwargs={'pk': self.object.pk})
        else:
            return reverse_lazy('libtekin:location-detail', kwargs={'pk': self.object.pk})

class LocationUpdate(PermissionRequiredMixin, UpdateView):
    permission_required = 'libtekin.change_location'
    model = Location
    form_class = LocationForm

    def get_success_url(self):
        return reverse_lazy('libtekin:location-detail', kwargs={'pk': self.object.pk})

class LocationDetail(PermissionRequiredMixin, DetailView):
    permission_required = 'libtekin.view_location'
    model = Location

class LocationDelete(PermissionRequiredMixin, DeleteView):
    permission_required = 'libtekin.delete_location'
    model = Location
    success_url = reverse_lazy('libtekin:location-list')

class LocationList(PermissionRequiredMixin, ListView):
    permission_required = 'libtekin.view_location'
    model = Location

class LocationClose(PermissionRequiredMixin, DetailView):
    permission_required = 'libtekin.view_location'
    model = Location
    template_name = 'libtekin/location_closer.html'

class EntityCreate(PermissionRequiredMixin, CreateView):
    permission_required = 'libtekin.add_entity'
    model = Entity
    form_class = EntityForm

    def get_success_url(self):
        if 'opener' in self.request.POST and self.request.POST['opener'] > '':
            return reverse_lazy('libtekin:entity-close', kwargs={'pk': self.object.pk})
        else:
            return reverse_lazy('libtekin:entity-detail', kwargs={'pk': self.object.pk})

class EntityUpdate(PermissionRequiredMixin, UpdateView):
    permission_required = 'libtekin.change_entity'
    model = Entity
    form_class = EntityForm

    def get_success_url(self):
        return reverse_lazy('libtekin:entity-detail', kwargs={'pk': self.object.pk})


class EntityDetail(PermissionRequiredMixin, DetailView):
    permission_required = 'libtekin.view_entity'
    model = Entity

class EntityDelete(PermissionRequiredMixin, DeleteView):
    permission_required = 'libtekin.delete_entity'
    model = Entity
    success_url = reverse_lazy('libtekin:entity-list')

class EntityList(PermissionRequiredMixin, ListView):
    permission_required = 'libtekin.view_entity'
    model = Entity

class EntityClose(PermissionRequiredMixin, DetailView):
    permission_required = 'libtekin.view_entity'
    model = Entity
    template_name = 'libtekin/entity_closer.html'

def get_primary_id_field( request, mmodel_id):
    try:
        return Mmodel.objects.get(pk=mmodel_id).primary_id_field
    except ObjectDoesNotExist:
        return None

