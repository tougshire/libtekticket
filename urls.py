from django.urls import path
from . import views

app_name = 'libtekticket'

urlpatterns = [
    path('ticket/create/', views.TicketCreate.as_view(), name='ticket-create'),
    path('ticket/<int:pk>/update/', views.TicketUpdate.as_view(), name='ticket-update'),
    path('ticket/<int:pk>/detail/', views.TicketDetail.as_view(), name='ticket-detail'),
    path('ticket/<int:pk>/delete/', views.TicketSoftDelete.as_view(), name='ticket-delete'),
    path('ticket/list/', views.TicketList.as_view(), name='ticket-list'),
    path('ticketnote/<int:ticket>/create/', views.TicketNoteCreate.as_view(), name='ticketnote-create'),
]
