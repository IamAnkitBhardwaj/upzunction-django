"""
URL configuration for upzunction project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
"""
from django.contrib import admin
from django.urls import path, include
from social import views
urlpatterns = [
    path('admin/', admin.site.urls),

    
    
    # This correctly imports all the pre-built auth URLs like login/logout.
    path('accounts/', include('django.contrib.auth.urls')),
   
    # This correctly imports all of your app's URLs from social/urls.py,
    # including the new OTP registration URLs.
    path('', include('social.urls')),


    
]
