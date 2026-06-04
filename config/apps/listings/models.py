from django.db import models
from django.conf import settings
from PIL import Image as PilImage
from django.utils.text import slugify
import uuid
import os

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
    is_approved = models.BooleanField(default=False)
    slug = models.SlugField(max_length=255,unique=True,blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='liked_listings', blank=True)

    def save(self,*args,**kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            if Listing.objects.filter(slug=slug).exclude(id=self.id).exists():
                slug = f'{base_slug}-{uuid.uuid4().hex[:6]}'
            self.slug = slug
        super().save(*args,**kwargs)

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

    def save(self,*args,**kwargs):
        super().save(*args,**kwargs)
        self.compress()
    
    def compress(self):
        img = PilImage.open(self.image.path)
        if img.mode in ('RGBA','P'):
            img.convert('RGB')

        max_width = 1200
        if img.width > max_width:
            ratio = max_width/img.width
            new_height = int(img.height*ratio)
            img = img.resize((max_width, new_height), PilImage.Resampling.LANCZOS)

        img.save(self.image.path, 'JPEG', quality=85, optimize=True)

    def __str__(self):
        return f'({self.listing})-({self.id})'