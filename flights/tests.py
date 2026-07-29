from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Airport, Booking, Flight
from .services import NotEnoughSeats, book_flight


class FlightBookingTests(TestCase):
    def setUp(self):
        self.kyiv = Airport.objects.create(
            name="Boryspil International Airport",
            city="Kyiv",
            country="Ukraine",
            code="KBP",
        )
        self.paris = Airport.objects.create(
            name="Charles de Gaulle Airport",
            city="Paris",
            country="France",
            code="CDG",
        )
        self.flight = Flight.objects.create(
            departure_airport=self.kyiv,
            arrival_airport=self.paris,
            departure_time=timezone.now() + timezone.timedelta(days=3),
            arrival_time=timezone.now() + timezone.timedelta(days=3, hours=3),
            airline="SkyWay",
            aircraft="Airbus A320",
            price="180.00",
            available_seats=2,
        )

    def test_booking_decreases_available_seats(self):
        booking = book_flight(
            flight_id=self.flight.id,
            full_name="Olena Kovalenko",
            email="olena@example.com",
            seats=1,
        )

        self.flight.refresh_from_db()

        self.assertEqual(booking.seats, 1)
        self.assertEqual(self.flight.available_seats, 1)

    def test_booking_rejects_oversell(self):
        with self.assertRaises(NotEnoughSeats):
            book_flight(
                flight_id=self.flight.id,
                full_name="Ivan Bondar",
                email="ivan@example.com",
                seats=3,
            )

        self.assertEqual(Booking.objects.count(), 0)

    def test_search_by_city(self):
        response = self.client.get(reverse("flights:flight_list"), {"origin": "Kyiv"})

        self.assertContains(response, "SkyWay")
        self.assertContains(response, "KBP")

    def test_booking_view_creates_booking(self):
        response = self.client.post(
            reverse("flights:flight_detail", args=[self.flight.id]),
            {
                "full_name": "Marta Shevchenko",
                "email": "marta@example.com",
                "seats": 2,
            },
        )

        self.flight.refresh_from_db()

        booking = Booking.objects.get()

        self.assertRedirects(response, reverse("flights:booking_confirmation", args=[booking.id]))
        self.assertEqual(Booking.objects.count(), 1)
        self.assertEqual(self.flight.available_seats, 0)
