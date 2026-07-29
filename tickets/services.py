"""
=============================================================
  ПРАКТИЧНЕ ЗАВДАННЯ ДЛЯ СТУДЕНТІВ — детальний опис у README.md
=============================================================

Функція purchase_seat() нижче симулює продаж квитків на концерт.
Зараз вона працює НЕПРАВИЛЬНО: якщо двоє покупців одночасно
намагаються купити останнє вільне місце, система може продати
БІЛЬШЕ квитків, ніж їх насправді є (це називається "оверселлінг",
overselling — класичний приклад race condition, гонки умов).

ВАШЕ ЗАВДАННЯ:
  1. Обгорнути логіку функції в transaction.atomic()
  2. Замінити Concert.objects.get(...) на
     Concert.objects.select_for_update().get(...)
     — це "заблокує" рядок концерту в БД, поки транзакція не завершиться,
     і другий покупець буде змушений почекати своєї черги.
  3. Запустити тести: python manage.py test tickets
     Тест повинен стати зеленим (зараз він падає).
"""
import time

from .models import Booking, Concert

# Штучна затримка ТІЛЬКИ для навчальної демонстрації race condition:
# вона імітує час обробки платежу і робить гонку умов помітною та
# відтворюваною. У реальному проєкті такого рядка, звісно, не буде.
SIMULATED_PAYMENT_DELAY = 0.3


class NotEnoughSeats(Exception):
    pass


def purchase_seat(concert_id, customer_name, seats_requested=1):
    """Купує seats_requested місць на концерт concert_id.

    Повертає створений Booking, або кидає NotEnoughSeats,
    якщо вільних місць не вистачає.
    """
    # --- TODO: тут потрібно додати transaction.atomic() ---
    # --- TODO: тут потрібно замінити get() на select_for_update().get() ---
    concert = Concert.objects.get(id=concert_id)

    if concert.seats_left < seats_requested:
        raise NotEnoughSeats("Недостатньо вільних місць")

    time.sleep(SIMULATED_PAYMENT_DELAY)  # тут і виникає гонка умов

    concert.seats_booked += seats_requested
    concert.save()

    return Booking.objects.create(
        concert=concert,
        customer_name=customer_name,
        seats=seats_requested,
    )
