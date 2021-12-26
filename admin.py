from django.contrib import admin
from .models import Ticket, Technician, TicketNote

admin.site.register(Ticket)

admin.site.register(Technician)

admin.site.register(TicketNote)
