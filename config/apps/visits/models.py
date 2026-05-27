from django.db import models
from django.conf import settings
from apps.listings.models import Listing

# Create your models here.
class Visit(models.Model):
    STATUS = [
        ('En attente', 'En attente'),
        ('Acceptée', 'Acceptée'),
        ('Refusée', 'Refusée'),
    ]
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='visits')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='visits_sent')
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='visits_received')
    status = models.CharField(max_length=20, choices=STATUS, default='En attente')
    date = models.DateTimeField()
    message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.sender} → {self.listing} ({self.date})"