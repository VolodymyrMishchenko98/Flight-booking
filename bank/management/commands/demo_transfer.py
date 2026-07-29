"""
Навчальна демонстрація: transaction.atomic() на прикладі переказу грошей.

Запуск:
    python manage.py demo_transfer
"""
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction

from bank.models import Account


def print_balances(stdout, title):
    stdout.write(f"\n--- {title} ---")
    for acc in Account.objects.all():
        stdout.write(f"  {acc.name}: {acc.balance} грн")


def transfer_broken(from_acc, to_acc, amount):
    """ПОГАНИЙ приклад: без транзакції.

    Якщо після першого save() станеться помилка — гроші вже
    списані з from_acc, але so to_acc так і не отримає їх.
    Дані в БД лишаються неконсистентними.
    """
    from_acc.balance -= amount
    from_acc.save()

    raise Exception("Симуляція збою (наприклад, обвал сервера)")

    to_acc.balance += amount  # pragma: no cover - ніколи не виконається
    to_acc.save()


@transaction.atomic
def transfer_safe(from_acc, to_acc, amount):
    """ДОБРИЙ приклад: з transaction.atomic().

    Якщо всередині блоку виникає необроблене виключення — Django
    автоматично відкатить (rollback) УСІ зміни, включно з тим
    save(), що вже "виконався".
    """
    from_acc.balance -= amount
    from_acc.save()

    raise Exception("Симуляція збою (наприклад, обвал сервера)")

    to_acc.balance += amount  # pragma: no cover - ніколи не виконається
    to_acc.save()


class Command(BaseCommand):
    help = "Демонструє різницю між переказом грошей БЕЗ і З transaction.atomic()"

    def handle(self, *args, **options):
        Account.objects.all().delete()
        alice = Account.objects.create(name="Alice", balance=Decimal("1000"))
        bob = Account.objects.create(name="Bob", balance=Decimal("500"))

        print_balances(self.stdout, "Початкові баланси")

        self.stdout.write(self.style.WARNING(
            "\n>>> Переказ 200 грн від Alice до Bob БЕЗ transaction.atomic()"
        ))
        try:
            transfer_broken(alice, bob, Decimal("200"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Виникла помилка: {e}"))

        alice.refresh_from_db()
        bob.refresh_from_db()
        print_balances(self.stdout, "Баланси ПІСЛЯ (гроші зникли в нікуди!)")

        # Скидаємо баланси до початкових значень
        alice.balance = Decimal("1000")
        alice.save()
        bob.balance = Decimal("500")
        bob.save()

        self.stdout.write(self.style.WARNING(
            "\n>>> Переказ 200 грн від Alice до Bob З transaction.atomic()"
        ))
        try:
            transfer_safe(alice, bob, Decimal("200"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Виникла помилка: {e}"))

        alice.refresh_from_db()
        bob.refresh_from_db()
        print_balances(self.stdout, "Баланси ПІСЛЯ (усе відкотилось назад!)")

        self.stdout.write(self.style.SUCCESS(
            "\nВисновок: без atomic() гроші губляться, з atomic() — БД лишається консистентною.\n"
        ))
