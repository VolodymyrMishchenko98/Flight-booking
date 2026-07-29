"""
Тест-демонстрація race condition при купівлі останнього квитка.

Симулюємо двох покупців, які ОДНОЧАСНО намагаються купити останнє
вільне місце на концерт. Правильна реалізація purchase_seat() (з
transaction.atomic() + select_for_update()) повинна пропустити рівно
ОДНОГО покупця, а другому — коректно відмовити.

Поки функція не виправлена, цей тест буде падати — купівля пройде
в обох, і система "продасть" квиток, якого вже не існує.
"""
import threading

from django.db import OperationalError, connections
from django.test import TransactionTestCase

from .models import Concert
from .services import NotEnoughSeats, purchase_seat


class OversellingTest(TransactionTestCase):

    def setUp(self):
        self.concert = Concert.objects.create(
            title="Тестовий концерт", total_seats=10, seats_booked=9
        )

    def test_only_one_buyer_gets_last_seat(self):
        results = []

        def buy(customer_name):
            try:
                purchase_seat(self.concert.id, customer_name, 1)
                results.append("ok")
            except NotEnoughSeats:
                results.append("declined")
            except OperationalError:
                # SQLite блокує весь файл БД, а не окремий рядок (на
                # відміну від PostgreSQL/MySQL), тож другий покупець
                # інколи отримує саме таку помилку замість чистого
                # NotEnoughSeats. Головне для нас — оверселлінгу нема.
                results.append("declined")
            finally:
                # кожен потік має закрити своє з'єднання з БД
                connections.close_all()

        t1 = threading.Thread(target=buy, args=("Іван",))
        t2 = threading.Thread(target=buy, args=("Марія",))
        t1.start()
        t2.start()
        t1.join()
        t2.join()

        self.concert.refresh_from_db()

        self.assertLessEqual(
            self.concert.bookings.count(),
            1,
            "Оверселлінг! Продано більше квитків, ніж було вільних місць — "
            "race condition ще не виправлено.",
        )
        self.assertEqual(
            results.count("ok"),
            1,
            "Має бути рівно ОДИН успішний покупець і одна відмова.",
        )
