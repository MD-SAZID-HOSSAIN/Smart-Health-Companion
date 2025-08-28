from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class ProfileForm(forms.ModelForm):
    age = forms.IntegerField(
        required=False,
        min_value=1,
        max_value=120,
        help_text="Enter your age (1-120)"
    )
    height = forms.FloatField(
        required=False,
        min_value=50.0,
        max_value=300.0,
        help_text="Enter your height in cm (50-300)"
    )
    weight = forms.FloatField(
        required=False,
        min_value=20.0,
        max_value=500.0,
        help_text="Enter your weight in kg (20-200)"
    )

    class Meta:
        model = Profile
        fields = ['age', 'height', 'weight']

