from django.db import models
from apps.listings.models import Listing
from django.conf import settings

# Create your models here.
class Report(models.Model):
    REASONS = [
        ('Contenu inapproprié', 'Contenu inapproprié'),
        ('Arnaque', 'Arnaque'),
        ('Fausse annonce', 'Fausse annonce'),
        ('Comportement abusif', 'Comportement abusif'),
        ('Autre', 'Autre'),
    ]

    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reports_sent')
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='reports', null=True, blank=True)
    reported_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reports_received', null=True, blank=True)
    reason = models.CharField(max_length=50, choices=REASONS)
    message = models.TextField(blank=True)
    is_resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Signalement de {self.author.username} — {self.reason}'