from django.core.exceptions import ValidationError
from django.db import models


class Airport(models.Model):
    name = models.CharField(max_length=160)
    city = models.CharField(max_length=120)
    country = models.CharField(max_length=120)
    code = models.CharField(max_length=3, unique=True, help_text="IATA code")

    class Meta:
        ordering = ["city", "code"]

    def clean(self):
        if self.code:
            self.code = self.code.upper()
            if len(self.code) != 3 or not self.code.isalpha():
                raise ValidationError({"code": "IATA code must contain exactly 3 letters."})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.city} ({self.code})"


class Flight(models.Model):
    departure_airport = models.ForeignKey(
        Airport,
        on_delete=models.CASCADE,
        related_name="departing_flights",
    )
    arrival_airport = models.ForeignKey(
        Airport,
        on_delete=models.CASCADE,
        related_name="arriving_flights",
    )
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    airline = models.CharField(max_length=120)
    aircraft = models.CharField(max_length=120)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    available_seats = models.PositiveIntegerField()

    class Meta:
        ordering = ["departure_time", "price"]

    @property
    def duration(self):
        return self.arrival_time - self.departure_time

    @property
    def route(self):
        return f"{self.departure_airport.code} -> {self.arrival_airport.code}"

    def clean(self):
        errors = {}
        if self.departure_airport_id and self.arrival_airport_id:
            if self.departure_airport_id == self.arrival_airport_id:
                errors["arrival_airport"] = "Arrival airport must differ from departure airport."
        if self.departure_time and self.arrival_time:
            if self.arrival_time <= self.departure_time:
                errors["arrival_time"] = "Arrival time must be later than departure time."
        if errors:
            raise ValidationError(errors)

    def __str__(self):
        return f"{self.airline}: {self.route} at {self.departure_time:%Y-%m-%d %H:%M}"


class Booking(models.Model):
    full_name = models.CharField(max_length=160)
    email = models.EmailField()
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE, related_name="bookings")
    seats = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def clean(self):
        if self.seats < 1:
            raise ValidationError({"seats": "Book at least one seat."})

    def __str__(self):
        return f"{self.full_name} - {self.seats} seat(s) on {self.flight.route}"
