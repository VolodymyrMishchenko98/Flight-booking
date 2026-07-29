from django.db import models


class Concert(models.Model):
    title = models.CharField(max_length=200)
    total_seats = models.PositiveIntegerField()
    seats_booked = models.PositiveIntegerField(default=0)

    @property
    def seats_left(self):
        return self.total_seats - self.seats_booked

    def __str__(self):
        return f"{self.title} ({self.seats_left}/{self.total_seats} вільно)"


class Booking(models.Model):
    concert = models.ForeignKey(Concert, on_delete=models.CASCADE, related_name="bookings")
    customer_name = models.CharField(max_length=100)
    seats = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.customer_name} — {self.seats} місць на {self.concert.title}"
