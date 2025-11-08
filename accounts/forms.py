from django import forms
from .models import User
from core.models import UserProfile

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    role = forms.ChoiceField(choices=[
        (User.Role.RESTAURANT, 'Restaurant'),
        (User.Role.NGO, 'NGO'),
        (User.Role.EVENTPLANNER, 'Event Planner'),
    ])

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'role']

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['address', 'contact_number', 'profile_picture'] 