from django import forms
from .models import Bhandara

class BhandaraSubmitForm(forms.ModelForm):
    class Meta:
        model = Bhandara
        # We ONLY want the public to fill out these specific fields
        fields = ['google_maps_url', 'area_name', 'organizer_name', 'business_name', 'menu_details']
        
        widgets = {
            'google_maps_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Paste Google Maps Share Link Here...', 'required': True}),
            'area_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Alambagh, Gomti Nagar...'}),
            'organizer_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your Name (Optional)'}),
            'business_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Business/Shop Name (Optional)'}),
            'menu_details': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Poori-Sabzi, Halwa (Optional)'}),
        }