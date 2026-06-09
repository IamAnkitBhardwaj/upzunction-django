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
    path(
    'add/',
    views.add_tourist_spot,
    name='add_spot'
),
path(
    'edit/<int:spot_id>/',
    views.edit_tourist_spot,
    name='edit_spot'
),

path(
    'delete/<int:spot_id>/',
    views.delete_tourist_spot,
    name='delete_spot'
),

path(
    'spot/<int:spot_id>/',
    views.tourist_spot_detail,
    name='spot_detail'
),

]