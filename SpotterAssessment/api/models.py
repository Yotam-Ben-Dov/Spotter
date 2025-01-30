from django.db import models

class FuelStation(models.Model):
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    lat = models.FloatField()
    lon = models.FloatField()
    price = models.FloatField()  # price per gallon

    def __str__(self):
        return self.name
