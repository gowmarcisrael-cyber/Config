from django.db import models
from django.conf import settings

# Create your models here.

class Notification(models.Model):
    TYPES = [
        ('visit_accepted', 'Visite acceptée'),
        ('visit_refused', 'Visite refusée'),
        ('visit_cancelled', 'Visite annulée'),
        ('listing_approved', 'Annonce approuvée'),
        ('new_message', 'Nouveau message'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=30, choices=TYPES)
    message = models.CharField(max_length=255)
    link = models.CharField(max_length=255, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.username} — {self.message[:30]}'