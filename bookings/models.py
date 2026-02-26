from django.db import models
import uuid
from django.utils import timezone
from datetime import timedelta


# Create your models here.

class Ticket(models.Model):
    ticket_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    source = models.CharField(max_length=100)
    destination = models.CharField(max_length=100)

    passengers = models.PositiveIntegerField(default=1)

    fare_per_person = models.PositiveIntegerField()
    total_fare = models.PositiveIntegerField()

    stations = models.JSONField()        # route stations snapshot
    distance = models.PositiveIntegerField()
    interchanges = models.PositiveIntegerField()
    travel_time = models.PositiveIntegerField()

    booking_time = models.DateTimeField(auto_now_add=True)
    valid_until = models.DateTimeField(default=timezone.now)
          
    is_used = models.BooleanField(default=False)

    status = models.CharField(
        max_length=20,
        choices=[
            ("PENDING", "PENDING"),
            ("CONFIRMED", "CONFIRMED"),
            ("CANCELLED", "CANCELLED"),
            ("FAILED", "FAILED"),
        ],
        default="PENDING"
    )

    def __str__(self):
        return f"{self.ticket_id} | {self.source} → {self.destination}"



class Payment(models.Model):
    payment_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    ticket = models.OneToOneField(Ticket, on_delete=models.CASCADE)

    amount = models.PositiveIntegerField()

    status = models.CharField(
        max_length=20,
        choices=[
            ("INITIATED", "INITIATED"),
            ("SUCCESS", "SUCCESS"),
            ("FAILED", "FAILED"),
        ],
        default="INITIATED"
    )

    transaction_id = models.CharField(max_length=200, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    
    
    
# payment History model...
class PaymentHistory(models.Model):
    
    STATUS_CHOICES = [
        ("SUCCESS", "SUCCESS"),
        ("FAILED", "FAILED"),
        ("REFUNDED", "REFUNDED"),
    ]

    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE)
    amount = models.IntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    
