from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.

class User(AbstractUser):
    profile = models.ImageField(upload_to='profile/',blank=True,null=True)
    def __str__(self):
        return self.username