from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    ROLE_CHOICES = (
        ("user", "User"),
        ("admin", "Admin"),
        ("manager", "Manager"),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    full_name = models.CharField(max_length=200)
    birth_year = models.PositiveIntegerField(null=True, blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="user")
    card_last4 = models.CharField(max_length=4, blank=True)

    def __str__(self) -> str:
        return f"{self.full_name} ({self.user.username})"


