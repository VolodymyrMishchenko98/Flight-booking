from django.db import transaction

from .models import Booking, Flight


class NotEnoughSeats(Exception):
    pass


def book_flight(*, flight_id, full_name, email, seats, user=None):
    with transaction.atomic():
        flight = Flight.objects.select_for_update().get(id=flight_id)

        if flight.available_seats < seats:
            raise NotEnoughSeats("Not enough seats available for this flight.")

        flight.available_seats -= seats
        flight.save(update_fields=["available_seats"])

        booking = Booking.objects.create(
            user=user,
            flight=flight,
            full_name=full_name,
            email=email,
            seats=seats,
        )
        return booking
