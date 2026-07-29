from django.contrib import admin

from .models import Airport, Booking, Flight


@admin.register(Airport)
class AirportAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "city", "country")
    search_fields = ("code", "name", "city", "country")
    ordering = ("city", "code")


@admin.register(Flight)
class FlightAdmin(admin.ModelAdmin):
    list_display = (
        "airline",
        "route",
        "departure_time",
        "arrival_time",
        "price",
        "available_seats",
    )
    list_filter = ("airline", "departure_airport", "arrival_airport")
    search_fields = (
        "airline",
        "aircraft",
        "departure_airport__city",
        "arrival_airport__city",
        "departure_airport__code",
        "arrival_airport__code",
    )
    autocomplete_fields = ("departure_airport", "arrival_airport")
    date_hierarchy = "departure_time"


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("full_name", "email", "flight", "seats", "created_at")
    list_filter = ("created_at", "flight__airline")
    search_fields = ("full_name", "email", "flight__airline")
    readonly_fields = ("created_at",)
