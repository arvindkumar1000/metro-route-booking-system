from django.contrib.auth.models import AbstractUser
from django.db import models


# Create your models here.

class User(AbstractUser):
    ROLE_CHOICES = (
        ('ADMIN','Admin'),
        ('STAFF','staff'),
        ('CUSTOMER','Customer'),
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES,default='CUSTOMER')
    
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    
    
    def __str__(self):
        return self.username
    
        