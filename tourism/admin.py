from django.contrib import admin
from .models import State, City, TouristSpot


@admin.register(State)
class StateAdmin(admin.ModelAdmin):
    search_fields = ['name']


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ['name', 'state']
    list_filter = ['state']
    search_fields = ['name']


@admin.register(TouristSpot)
class TouristSpotAdmin(admin.ModelAdmin):

    list_display = [
        'name',
        'city',
        'rating',
        'views',
        'is_active'
    ]

    list_filter = [
        'city',
        'city__state',
        'is_active'
    ]

    search_fields = [
        'name',
        'area_name'
    ]