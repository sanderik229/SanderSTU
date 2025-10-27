from django.db import models


class Blogger(models.Model):
    SOCIAL_CHOICES = (
        ("instagram", "Instagram"),
        ("tiktok", "TikTok"),
        ("youtube", "YouTube"),
        ("vk", "VK"),
        ("telegram", "Telegram"),
    )
    name = models.CharField(max_length=200)
    social_network = models.CharField(max_length=30, choices=SOCIAL_CHOICES)
    topic = models.CharField(max_length=120)
    audience_size = models.PositiveIntegerField(default=0)

    def __str__(self) -> str:
        return f"{self.name} ({self.social_network})"


class AdOffer(models.Model):
    blogger = models.ForeignKey(Blogger, on_delete=models.CASCADE, related_name="offers")
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)

    def __str__(self) -> str:
        return f"{self.title} — {self.blogger.name}"


