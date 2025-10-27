from django.db import models
from django.contrib.auth.models import User
from bloggers.models import AdOffer


class Category(models.Model):
    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=140, unique=True)

    def __str__(self) -> str:
        return self.name


class Order(models.Model):
    STATUS_CHOICES = (
        ("new", "New"),
        ("paid", "Paid"),
        ("in_progress", "In progress"),
        ("done", "Done"),
        ("cancelled", "Cancelled"),
    )
    ORDER_TYPE_CHOICES = (
        ("offer", "Offer"),
        ("personal", "Personal"),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders", null=True, blank=True)
    offer = models.ForeignKey(AdOffer, on_delete=models.PROTECT, related_name="orders", null=True, blank=True)
    order_type = models.CharField(max_length=20, choices=ORDER_TYPE_CHOICES, default="personal")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="new")
    performance = models.JSONField(default=dict, blank=True)  # эффективность: показы, переходы, ctr
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Personal order fields
    full_name = models.CharField(max_length=200, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=40, blank=True)
    ad_type = models.CharField(max_length=50, blank=True)
    budget = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    description = models.TextField(blank=True)
    
    # Offer order fields
    deadline = models.PositiveIntegerField(null=True, blank=True, help_text="Срок выполнения в днях")
    requirements = models.TextField(blank=True, help_text="Дополнительные требования")

    def __str__(self) -> str:
        return f"Order #{self.id} by {self.user.username if self.user else self.full_name}"


