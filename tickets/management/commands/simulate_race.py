"""
Наочна демонстрація race condition для показу студентам НА ЛЕКЦІЇ
(перед видачею практичного завдання). Використовує ту саму механіку,
що й тест tickets/tests.py, але друкує результат у консоль.

Запуск:
    python manage.py simulate_race
"""
import threading
import time

from django.core.management.base import BaseCommand
from django.db import OperationalError, connections, transaction

from tickets.models import Booking, Concert
from tickets.services import NotEnoughSeats, SIMULATED_PAYMENT_DELAY


def buy_without_lock(concert_id, customer_name, log):
    """Так само, як зараз написано в tickets/services.py — без захисту."""
    try:
        concert = Concert.objects.get(id=concert_id)
        if concert.seats_left < 1:
            log.append(f"  [{customer_name}] ВІДМОВА — місць немає")
            return
        time.sleep(SIMULATED_PAYMENT_DELAY)
        concert.seats_booked += 1
        concert.save()
        Booking.objects.create(concert=concert, customer_name=customer_name, seats=1)
        log.append(f"  [{customer_name}] УСПІХ — квиток куплено")
    finally:
        connections.close_all()


def buy_with_lock(concert_id, customer_name, log):
    """Правильна версія — саме таку студенти мають написати самі."""
    try:
        with transaction.atomic():
            concert = Concert.objects.select_for_update().get(id=concert_id)
            if concert.seats_left < 1:
                log.append(f"  [{customer_name}] ВІДМОВА — місць немає")
                return
            time.sleep(SIMULATED_PAYMENT_DELAY)
            concert.seats_booked += 1
            concert.save()
            Booking.objects.create(concert=concert, customer_name=customer_name, seats=1)
            log.append(f"  [{customer_name}] УСПІХ — квиток куплено")
    except OperationalError:
        # SQLite блокує весь файл БД, а не окремий рядок — на відміну
        # від PostgreSQL/MySQL. У продакшн-БД тут просто буде коротке
        # очікування, а не помилка.
        log.append(f"  [{customer_name}] ВІДМОВА — БД зайнята іншою транзакцією")
    finally:
        connections.close_all()


class Command(BaseCommand):
    help = "Демонструє race condition при купівлі останнього квитка на концерт"

    def run_round(self, title, buy_func):
        Concert.objects.all().delete()
        concert = Concert.objects.create(
            title="Океан Ельзи — прощальний тур", total_seats=10, seats_booked=9
        )
        seats_available_before = concert.seats_left

        self.stdout.write(self.style.WARNING(f"\n>>> {title}"))
        self.stdout.write(
            f"Залишилось {seats_available_before} місце. Два покупці тиснуть 'Купити' одночасно:"
        )

        log = []
        t1 = threading.Thread(target=buy_func, args=(concert.id, "Іван", log))
        t2 = threading.Thread(target=buy_func, args=(concert.id, "Марія", log))
        t1.start()
        t2.start()
        t1.join()
        t2.join()

        for line in log:
            self.stdout.write(line)

        concert.refresh_from_db()
        sold = concert.bookings.count()
        self.stdout.write(
            f"Доступно було: {seats_available_before} місце. "
            f"Успішних покупок: {sold}. Лічильник seats_booked у БД: {concert.seats_booked}."
        )
        if sold > seats_available_before:
            self.stdout.write(self.style.ERROR(
                "ОВЕРСЕЛЛІНГ! Продано більше квитків, ніж було вільних місць насправді."
            ))
        else:
            self.stdout.write(self.style.SUCCESS("Все коректно — оверселлінгу немає."))

    def handle(self, *args, **options):
        self.run_round(
            "Без transaction.atomic() + select_for_update() (як зараз у services.py)",
            buy_without_lock,
        )
        self.run_round(
            "З transaction.atomic() + select_for_update() (те, що треба зробити)",
            buy_with_lock,
        )
