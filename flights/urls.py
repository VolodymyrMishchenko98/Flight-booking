from django.urls import path

from . import views

app_name = "flights"

urlpatterns = [
    path("", views.flight_list, name="flight_list"),
    path("flights/<int:pk>/", views.flight_detail, name="flight_detail"),
    path("bookings/<int:pk>/", views.booking_confirmation, name="booking_confirmation"),
]
