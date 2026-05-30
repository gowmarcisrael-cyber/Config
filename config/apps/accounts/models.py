from django.db import models
from django.contrib.auth.models import AbstractUser
from PIL import Image as PilImage
# Create your models here.

class User(AbstractUser):
    avatar = models.ImageField(upload_to='profile/',blank=True,null=True)
    def __str__(self):
        return self.username
    
    def save(self,*args,**kwargs):
        super().save(*args,**kwargs)
        if self.avatar:
            img = PilImage.open(self.avatar.path)
            if img.mode in ('RGBA','P'):
                img = img.convert('RGB')
            if img.width > 400:
                img = img.resize((400,400),PilImage.Resampling.LANCZOS)
            img.save(self.avatar.path, 'JPEG',quality=90,optimize=True)