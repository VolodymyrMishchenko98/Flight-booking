from django.core.management.base import BaseCommand
from django.utils import timezone

from flights.models import Airport, Flight


class Command(BaseCommand):
    help = "Create demo airports and flights for the airline booking project."

    def handle(self, *args, **options):
        airports = {
            "KBP": ("Boryspil International Airport", "Kyiv", "Ukraine"),
            "LWO": ("Lviv Danylo Halytskyi International Airport", "Lviv", "Ukraine"),
            "WAW": ("Warsaw Chopin Airport", "Warsaw", "Poland"),
            "CDG": ("Charles de Gaulle Airport", "Paris", "France"),
            "LHR": ("Heathrow Airport", "London", "United Kingdom"),
            "FCO": ("Leonardo da Vinci-Fiumicino Airport", "Rome", "Italy"),
        }

        airport_objects = {}
        for code, (name, city, country) in airports.items():
            airport, _ = Airport.objects.update_or_create(
                code=code,
                defaults={"name": name, "city": city, "country": country},
            )
            airport_objects[code] = airport

        now = timezone.now().replace(minute=0, second=0, microsecond=0)
        demo_flights = [
            ("SkyWay", "Boeing 737-800", "KBP", "CDG", 2, 7, 3, "189.00", 42),
            ("AeroNova", "Airbus A320neo", "KBP", "LHR", 4, 9, 3, "220.00", 18),
            ("Blue Horizon", "Embraer E195", "LWO", "WAW", 1, 6, 1, "92.00", 25),
            ("SkyWay", "Airbus A321", "WAW", "FCO", 3, 10, 2, "145.00", 9),
            ("Nordic Air", "Boeing 787-9", "LHR", "KBP", 5, 12, 3, "260.00", 31),
            ("AeroNova", "Airbus A320", "CDG", "LWO", 6, 15, 2, "174.00", 14),
            ("Blue Horizon", "Boeing 737 MAX 8", "KBP", "FCO", 8, 8, 2, "205.00", 6),
            ("Nordic Air", "Airbus A319", "WAW", "LHR", 7, 18, 2, "135.00", 33),
        ]

        created = 0
        for airline, aircraft, departure, arrival, days, hour, duration, price, seats in demo_flights:
            departure_time = now + timezone.timedelta(days=days, hours=hour)
            arrival_time = departure_time + timezone.timedelta(hours=duration)
            _, was_created = Flight.objects.update_or_create(
                airline=airline,
                aircraft=aircraft,
                departure_airport=airport_objects[departure],
                arrival_airport=airport_objects[arrival],
                departure_time=departure_time,
                defaults={
                    "arrival_time": arrival_time,
                    "price": price,
                    "available_seats": seats,
                },
            )
            created += int(was_created)

        self.stdout.write(self.style.SUCCESS(f"Demo data is ready. New flights: {created}"))
