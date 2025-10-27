from django.db import models
from django.contrib.auth.models import User
from ads.models import Order


class Transaction(models.Model):
    TYPE_CHOICES = (
        ("payment", "Payment"),
        ("refund", "Refund"),
    )
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="transactions")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="transactions")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default="payment")
    payload = models.JSONField(default=dict, blank=True)  # данные шлюза/эмуляции
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.type} {self.amount} for order {self.order_id}"


