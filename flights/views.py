from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import BookingForm, FlightSearchForm
from .models import Booking, Flight
from .services import NotEnoughSeats, book_flight


def flight_list(request):
    form = FlightSearchForm(request.GET or None)
    flights = Flight.objects.select_related("departure_airport", "arrival_airport")

    if form.is_valid():
        origin = form.cleaned_data.get("origin")
        destination = form.cleaned_data.get("destination")
        date = form.cleaned_data.get("date")
        airline = form.cleaned_data.get("airline")
        sort = form.cleaned_data.get("sort") or "departure"

        if origin:
            flights = flights.filter(
                Q(departure_airport__city__icontains=origin)
                | Q(departure_airport__name__icontains=origin)
                | Q(departure_airport__code__icontains=origin)
            )
        if destination:
            flights = flights.filter(
                Q(arrival_airport__city__icontains=destination)
                | Q(arrival_airport__name__icontains=destination)
                | Q(arrival_airport__code__icontains=destination)
            )
        if date:
            flights = flights.filter(departure_time__date=date)
        if airline:
            flights = flights.filter(airline=airline)

        order_map = {
            "departure": "departure_time",
            "price": "price",
            "-price": "-price",
            "seats": "-available_seats",
        }
        flights = flights.order_by(order_map.get(sort, "departure_time"))
    else:
        flights = flights.order_by("departure_time")

    airlines = Flight.objects.order_by("airline").values_list("airline", flat=True).distinct()
    paginator = Paginator(flights, 6)
    page = paginator.get_page(request.GET.get("page"))

    return render(
        request,
        "flights/flight_list.html",
        {
            "form": form,
            "page_obj": page,
            "airlines": airlines,
            "selected_airline": request.GET.get("airline", ""),
        },
    )


def flight_detail(request, pk):
    flight = get_object_or_404(
        Flight.objects.select_related("departure_airport", "arrival_airport"),
        pk=pk,
    )

    if request.method == "POST":
        if not request.user.is_authenticated:
            messages.error(request, "Please log in to book a flight.")
            return redirect("accounts:login")
        form = BookingForm(request.POST)
        if form.is_valid():
            try:
                booking = book_flight(
                    flight_id=flight.id,
                    full_name=form.cleaned_data["full_name"],
                    email=form.cleaned_data["email"],
                    seats=form.cleaned_data["seats"],
                )
            except NotEnoughSeats:
                messages.error(request, "There are not enough free seats for this booking.")
            else:
                messages.success(request, "Booking confirmed. Your ticket is ready.")
                return redirect("flights:booking_confirmation", pk=booking.pk)
        else:
            messages.error(request, "Please check the booking form.")
    else:
        form = BookingForm(initial={"seats": 1})

    return render(request, "flights/flight_detail.html", {"flight": flight, "form": form})


def booking_confirmation(request, pk):
    booking = get_object_or_404(
        Booking.objects.select_related(
            "flight",
            "flight__departure_airport",
            "flight__arrival_airport",
        ),
        pk=pk,
    )
    return render(request, "flights/booking_confirmation.html", {"booking": booking})
