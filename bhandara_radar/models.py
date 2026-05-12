from .utils import extract_coordinates
from django.db import models
from django.utils import timezone

class Bhandara(models.Model):
    # Location Details
    google_maps_url = models.URLField(max_length=500)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    area_name = models.CharField(max_length=100, blank=True, null=True)
    
    # Owner & Menu Details (Can be blank if submitted by random public)
    organizer_name = models.CharField(max_length=200, blank=True, null=True)
    business_name = models.CharField(max_length=200, blank=True, null=True)
    menu_details = models.CharField(max_length=255, blank=True, null=True)
    
    # Time & Status
    start_time = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    
    # ML / Crowd Status (Will be updated by our Random Forest model later)
    CROWD_CHOICES = (
        ('LOW', 'Moving Fast'),
        ('MODERATE', 'Moderate Rush'),
        ('HIGH', 'Heavy Rush'),
    )
    current_crowd_status = models.CharField(max_length=20, choices=CROWD_CHOICES, default='LOW')

    # Security & Admin Controls
    is_approved = models.BooleanField(default=False) # False = Hidden from public, True = Live
    is_verified_owner = models.BooleanField(default=False) # True = Gets the Blue Tick

    class Meta:
        verbose_name = 'Bhandara Location'
        verbose_name_plural = 'Bhandara Locations'

    def __str__(self):
        status = "🟢 Live" if self.is_approved else "🔴 Pending"
        return f"{self.area_name or 'Unknown'} | {status}"
    
    def save(self, *args, **kwargs):
        # If latitude and longitude are empty, but we have a URL, extract them!
        if self.google_maps_url and not (self.latitude and self.longitude):
            lat, lng = extract_coordinates(self.google_maps_url)
            if lat and lng:
                self.latitude = lat
                self.longitude = lng
        
        # Call the standard Django save process
        super().save(*args, **kwargs)