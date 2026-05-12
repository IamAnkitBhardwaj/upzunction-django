from django.urls import path
from . import views

app_name = 'bhandara_radar'

urlpatterns = [
    path('', views.bhandara_feed, name='feed'),
    path('add/', views.submit_bhandara, name='submit'),
    path('api/nearest/', views.api_nearest_bhandaras, name='api_nearest'),
]