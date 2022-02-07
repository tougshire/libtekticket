from django.contrib import admin
from .models import Ticket, Technician, TicketNote

class TicketAdmin(admin.ModelAdmin):
    list_display=('short_description', 'when', 'is_resolved')
    fields=(
        'item',
        'location',
        'short_description',
        'long_description',
        'urgency',
        'submitted_by',
        'when',
        'technician',
        'is_resolved',
        'resolution_notes',
        'recipient_emails'
    )

admin.site.register(Ticket, TicketAdmin)

class TechnicianAdmin(admin.ModelAdmin):
    list_display=('name', 'user')

admin.site.register(Technician, TechnicianAdmin)

admin.site.register(TicketNote)
