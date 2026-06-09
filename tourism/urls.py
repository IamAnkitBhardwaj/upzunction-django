from django.urls import path
from . import views

app_name = 'tourism'

urlpatterns = [

    path('', views.tourism_feed, name='feed'),

    path(
        'api/cities/',
        views.api_cities,
        name='api_cities'
    ),

    path(
        'api/spots/',
        views.api_tourist_spots,
        name='api_spots'
    ),

    path(
        'api/nearest/',
        views.api_nearest_tourist_spots,
        name='api_nearest'
    ),

]