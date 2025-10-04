# social/forms.py

from django import forms
from .models import Post
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm # Import this
from .models import Post, Profile
class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = [
            'title', 'description', 'location', 'is_location_specific',
            'phone_number', 'whatsapp_number'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Need a second-hand bicycle'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Describe your requirement in detail...'}),
            'location': forms.Select(attrs={'class': 'form-select'}),
            'is_location_specific': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Optional: 8877665544'}),
            'whatsapp_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Optional: 8877665544'}),
        }
        help_texts = {
            'is_location_specific': 'Check this box if your requirement is ONLY for the specific location you selected above. If unchecked, it will appear in the general Lucknow feed too.',
        }

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email']


class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email']

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['phone_number']