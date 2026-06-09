from django.db import models
from django.utils import timezone
from bhandara_radar.utils import extract_coordinates


class State(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class City(models.Model):
    state = models.ForeignKey(State,on_delete=models.CASCADE,related_name='cities'    )
    name = models.CharField(max_length=100)
    class Meta:
        unique_together = ('state', 'name')

    def __str__(self):
        return f"{self.name}, {self.state.name}"

class TouristSpot(models.Model):
    city = models.ForeignKey(City,on_delete=models.CASCADE,related_name='tourist_spots')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True,null=True)
    google_maps_url = models.URLField( max_length=500 )
    latitude = models.FloatField( blank=True,null=True)
    longitude = models.FloatField(blank=True,null=True)
    area_name = models.CharField(max_length=100,blank=True,null=True)
    image = models.ImageField(upload_to='tourism/spots/',blank=True,null=True)
    rating = models.FloatField(default=0)
    views = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField( default=timezone.now)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):

        if self.google_maps_url and not ( self.latitude and self.longitude):
            lat, lng = extract_coordinates(self.google_maps_url)
            if lat and lng:
                self.latitude = lat
                self.longitude = lng

        super().save(*args, **kwargs)