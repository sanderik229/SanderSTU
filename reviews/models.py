from django.db import models
from django.contrib.auth.models import User
from bloggers.models import Blogger, AdOffer


class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviews")
    blogger = models.ForeignKey(Blogger, on_delete=models.CASCADE, related_name="reviews")
    offer = models.ForeignKey(AdOffer, on_delete=models.SET_NULL, null=True, blank=True, related_name="reviews")
    rating = models.PositiveSmallIntegerField(default=5)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.user.username} → {self.blogger.name} ({self.rating})"


