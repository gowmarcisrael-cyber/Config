from django.db import models
from django.conf import settings

# Create your models here.
class Listing(models.Model):
    STATUS = [
        ('En vente', 'En vente'),
        ('A louer', 'A louer'),
        ('Vendu', 'Vendu'),
        ('Loué', 'Loué'),
    ]
    TYPES = [
        ('Appartement', 'Appartement'),
        ('Maison', 'Maison'),
        ('Local commercial', 'Local commercial'),
        ('Terrain', 'Terrain'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                            on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    property_type = models.CharField(max_length=20, choices=TYPES)
    status = models.CharField(max_length=20, choices=STATUS)
    price = models.DecimalField(max_digits=14,decimal_places=2)
    bathrooms = models.IntegerField()
    bedrooms = models.IntegerField()
    is_available = models.BooleanField(default=True)
    city = models.CharField(max_length=255)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    created_at = models.DateTimeField(auto_now_add=True)
    area = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    def __str__(self):
        return f'{self.title} - {self.id}'
    
    def get_first_image(self):
        first = self.images.first()
        return first.image.url if first else None
    
    class Meta:
        ordering = ['-created_at']
    
class Images(models.Model):
    listing = models.ForeignKey(Listing,on_delete=models.CASCADE, related_name='images') 
    image = models.ImageField(upload_to='listings/images/')

    class Meta:
        ordering = ['listing']

    def __str__(self):
        return f'({self.listing})-({self.id})'

class Favorite(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='favorites'
    )

    listing = models.ForeignKey(
        Listing,
        on_delete=models.CASCADE,
        related_name='favorites'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user','listing']