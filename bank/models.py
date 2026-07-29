from django.db import models


class Account(models.Model):
    """Простий банківський рахунок для демонстрації transaction.atomic()."""

    name = models.CharField(max_length=100)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.name}: {self.balance} грн"
