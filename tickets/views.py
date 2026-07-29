from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .services import NotEnoughSeats, purchase_seat


@csrf_exempt
def buy_tickets(request, concert_id):
    """Тонка HTTP-обгортка. Уся логіка — у services.purchase_seat()."""
    seats_requested = int(request.POST.get("seats", 1))
    customer_name = request.POST.get("customer_name", "Гість")

    try:
        booking = purchase_seat(concert_id, customer_name, seats_requested)
    except NotEnoughSeats:
        return JsonResponse({"error": "Недостатньо вільних місць"}, status=400)

    return JsonResponse({
        "status": "ok",
        "booking_id": booking.id,
        "seats_left": booking.concert.seats_left,
    })
