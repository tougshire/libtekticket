from django.contrib import admin
from .models import Ticket, Technician, TicketNote


admin.site.register(Ticket)

class TechnicianAdmin(admin.ModelAdmin):
    list_display=('name', 'user')

admin.site.register(Technician, TechnicianAdmin)

admin.site.register(TicketNote)
