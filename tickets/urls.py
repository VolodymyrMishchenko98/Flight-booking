from django.urls import path

from . import views

urlpatterns = [
    path("concerts/<int:concert_id>/buy/", views.buy_tickets, name="buy_tickets"),
]
