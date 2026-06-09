from django import forms
from .models import TouristSpot

class TouristSpotForm(forms.ModelForm):

    class Meta:

        model = TouristSpot

        fields = [
            'city',
            'name',
            'description',
            'google_maps_url',
            'image'
        ]

        widgets = {

            'city': forms.Select(
                attrs={
                    'class': 'form-select'
                }
            ),

            'name': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Enter tourist place name'
                }
            ),

            'description': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 5,
                    'placeholder': 'Describe this tourist place'
                }
            ),

            'google_maps_url': forms.URLInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Paste Google Maps URL'
                }
            ),

            'image': forms.FileInput(
                attrs={
                    'class': 'form-control'
                }
            ),
        }