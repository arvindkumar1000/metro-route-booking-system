from django.db import models

# Create your models here.

# stattion model (graph node)
class Station(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)
    line = models.CharField(max_length=50)
    
    
    
    def __str__(self):
        return f"{self.name} ({self.code})"
   


# connection model (graph edge)

class Connection(models.Model):
    source = models.ForeignKey(Station, related_name="source_connections", on_delete=models.CASCADE)
    destination = models.ForeignKey(Station, related_name="destination_connections", on_delete=models.CASCADE)

    distance = models.FloatField()   

    def __str__(self):
        return f"{self.source.code} → {self.destination.code}"


    