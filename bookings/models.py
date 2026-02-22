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
            ("CONFIRMED", "CONFIRMED"),
            ("CANCELLED", "CANCELLED")
        ],
        default="CONFIRMED"
    )

    def __str__(self):
        return f"{self.ticket_id} | {self.source} → {self.destination}"
