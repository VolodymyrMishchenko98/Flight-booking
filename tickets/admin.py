from django.contrib import admin
from .models import Concert, Booking


@admin.register(Concert)
class ConcertAdmin(admin.ModelAdmin):
    list_display = ("title", "total_seats", "seats_booked", "seats_left")


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("customer_name", "concert", "seats", "created_at")
