from django.views.generic.base import RedirectView
from django.urls import path, reverse_lazy
from . import views

app_name = 'libtekticket'

urlpatterns = [
    path('', RedirectView.as_view(url=reverse_lazy('libtekticket:ticket-list'))),
    path('ticket/', RedirectView.as_view(url=reverse_lazy('libtekticket:ticket-list'))),
    path('ticket/create/', views.TicketCreate.as_view(), name='ticket-create'),
    path('ticket/<int:pk>/update/', views.TicketUpdate.as_view(), name='ticket-update'),
    path('ticket/<int:pk>/detail/', views.TicketDetail.as_view(), name='ticket-detail'),
    path('ticket/<int:pk>/delete/', views.TicketSoftDelete.as_view(), name='ticket-delete'),
    path('ticket/list/', views.TicketList.as_view(), name='ticket-list'),
    path('ticket/<int:ticketpk>/ticketnote/create', views.TicketTicketNoteCreate.as_view(), name='ticketticketnote-create'),
]
