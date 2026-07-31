from django.contrib import messages
from django.contrib.auth import login
from django.shortcuts import redirect, render

from flights.models import Booking

from .forms import SignUpForm


def signup(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Account created successfully. Welcome to SkyDesk!")
            return redirect("flights:flight_list")
    else:
        form = SignUpForm()
    return render(request, "registration/signup.html", {"form": form})


def profile(request):
    bookings = (
        Booking.objects.filter(user=request.user)
        .select_related("flight", "flight__departure_airport", "flight__arrival_airport")
        .order_by("-created_at")
    )
    return render(request, "registration/profile.html", {"bookings": bookings})
