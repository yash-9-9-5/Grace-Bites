from django import forms
from .models import FoodDonation, FoodRequest, Collaboration, UserProfile, RestaurantProfile, NGOProfile, EventPlannerProfile
from django.contrib.auth import get_user_model

User = get_user_model()

class FoodDonationForm(forms.ModelForm):
    class Meta:
        model = FoodDonation
        fields = ['food_type', 'quantity', 'description', 'expiry_date', 'location', 'image']
        widgets = {
            'expiry_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class FoodRequestForm(forms.ModelForm):
    class Meta:
        model = FoodRequest
        fields = ['food_type', 'quantity_required', 'location', 'required_timing', 'description']
        widgets = {
            'required_timing': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class CollaborationForm(forms.ModelForm):
    class Meta:
        model = Collaboration
        fields = ['notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

class CollaborationCompletionForm(forms.ModelForm):
    class Meta:
        model = Collaboration
        fields = ['people_served']
        widgets = {
            'people_served': forms.NumberInput(attrs={'min': 1, 'required': True}),
        }

# Separate forms for each profile type
class RestaurantProfileForm(forms.ModelForm):
    class Meta:
        model = RestaurantProfile
        fields = ['restaurant_name', 'address', 'contact_number', 'profile_picture', 'cuisine_type', 'description', 'operating_hours']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class NGOProfileForm(forms.ModelForm):
    class Meta:
        model = NGOProfile
        fields = ['organization_name', 'address', 'contact_number', 'profile_picture', 'mission_statement', 'description', 'target_beneficiaries']
        widgets = {
            'mission_statement': forms.Textarea(attrs={'rows': 3}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class EventPlannerProfileForm(forms.ModelForm):
    class Meta:
        model = EventPlannerProfile
        fields = ['company_name', 'address', 'contact_number', 'profile_picture', 'specialization', 'description', 'years_of_experience']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

# Keep the old UserProfileForm for backward compatibility
class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['address', 'contact_number', 'profile_picture', 'organization_name', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        } 