from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from flights.models import Airport, Booking, Flight


class ProfilePageTests(TestCase):
    def test_profile_shows_user_bookings(self):
        user = get_user_model().objects.create_user(
            username="demo",
            email="demo@example.com",
            password="secret123",
            first_name="Demo",
            last_name="Traveler",
        )
        departure = Airport.objects.create(
            name="Main Airport",
            city="Kyiv",
            country="Ukraine",
            code="KBP",
        )
        arrival = Airport.objects.create(
            name="Central Airport",
            city="Warsaw",
            country="Poland",
            code="WAW",
        )
        flight = Flight.objects.create(
            departure_airport=departure,
            arrival_airport=arrival,
            departure_time="2026-08-10T08:00:00Z",
            arrival_time="2026-08-10T11:00:00Z",
            airline="SkyWay",
            aircraft="Boeing 737",
            price="180.00",
            available_seats=10,
        )
        Booking.objects.create(
            user=user,
            full_name="Demo Traveler",
            email=user.email,
            flight=flight,
            seats=2,
        )

        self.client.force_login(user)
        response = self.client.get(reverse("accounts:profile"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Your flights")
        self.assertContains(response, "SkyWay")
        self.assertContains(response, "KBP")
