from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import ensure_csrf_cookie
from django.http import HttpRequest
from django.contrib import messages
from django.db import transaction
from .forms import UserRegistrationForm, UserProfileForm
from core.models import UserProfile, FoodDonation, FoodRequest, Collaboration, Analysis, RestaurantProfile, NGOProfile, EventPlannerProfile

User = get_user_model()

@ensure_csrf_cookie
def register(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        profile_form = UserProfileForm(request.POST, request.FILES)
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save(commit=False)
            user.set_password(user_form.cleaned_data['password'])
            user.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()
            messages.success(request, 'Account created successfully! Please log in.')
            return redirect('login')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        user_form = UserRegistrationForm()
        profile_form = UserProfileForm()
    
    return render(request, 'registration/register.html', {
        'form': user_form,
        'profile_form': profile_form
    })

@ensure_csrf_cookie
def login_view(request: HttpRequest):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
    else:
        form = AuthenticationForm()
    
    return render(request, 'registration/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('home')

def dashboard(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    # Redirect to appropriate dashboard based on user role
    if request.user.role == User.Role.RESTAURANT:
        return redirect('restaurant_dashboard')
    elif request.user.role == User.Role.NGO:
        return redirect('ngo_dashboard')
    elif request.user.role == User.Role.EVENTPLANNER:
        return redirect('eventplanner_dashboard')
    else:
        return redirect('home')

@login_required
def delete_account(request):
    """Delete user account and all associated data"""
    if request.method == 'POST':
        confirm_text = request.POST.get('confirm_text', '')
        
        if confirm_text != 'DELETE':
            messages.error(request, 'Please type "DELETE" to confirm account deletion.')
            return render(request, 'accounts/delete_account_confirm.html')
        
        user = request.user
        
        # Use transaction to ensure all deletions happen or none
        with transaction.atomic():
            # Delete all food donations by this user
            FoodDonation.objects.filter(donor=user).delete()
            
            # Delete all food requests by this user
            FoodRequest.objects.filter(requester=user).delete()
            
            # Delete all collaborations involving this user
            Collaboration.objects.filter(donor=user).delete()
            Collaboration.objects.filter(ngo=user).delete()
            
            # Delete analysis data
            Analysis.objects.filter(user=user).delete()
            
            # Delete profile data
            try:
                if user.role == User.Role.RESTAURANT:
                    RestaurantProfile.objects.filter(user=user).delete()
                elif user.role == User.Role.NGO:
                    NGOProfile.objects.filter(user=user).delete()
                elif user.role == User.Role.EVENTPLANNER:
                    EventPlannerProfile.objects.filter(user=user).delete()
            except:
                pass
            
            # Try to delete old UserProfile if it exists
            try:
                UserProfile.objects.filter(user=user).delete()
            except:
                pass
            
            # Finally delete the user
            user.delete()
            
            messages.success(request, 'Your account and all data have been permanently deleted.')
            return redirect('home')
    
    return render(request, 'accounts/delete_account_confirm.html')

def debug_csrf(request):
    """Temporary debug view for CSRF issues"""
    if request.method == 'POST':
        return render(request, 'debug_csrf.html', {
            'message': 'CSRF token was valid!',
            'csrf_token': request.POST.get('csrfmiddlewaretoken', 'NOT FOUND'),
            'session_id': request.session.session_key
        })
    return render(request, 'debug_csrf.html', {
        'message': 'Please submit the form to test CSRF',
        'csrf_token': 'Not submitted yet',
        'session_id': request.session.session_key
    })


