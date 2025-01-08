from django.contrib import admin
from .models import *
# Register your models here.
class FlightAdmin(admin.ModelAdmin):
    list_display = ('flight_number', 'flight_class', 'available_seats', 'departure', 'arrival', 'price')
    list_filter = ('flight_class')
admin.site.register(Flight)
admin.site.register(Booking)
admin.site.register(Profile)
