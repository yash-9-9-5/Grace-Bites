from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model
from core.models import FoodDonation, FoodRequest, Collaboration, Analysis, NGOProfile, RestaurantProfile, EventPlannerProfile
from core.forms import FoodRequestForm, CollaborationForm, NGOProfileForm, CollaborationCompletionForm
from django.db.models import Count, Q

User = get_user_model()

@login_required
def ngo_dashboard(request):
    # Get all food posted by restaurants (always fetch fresh data)
    all_food_donations = FoodDonation.objects.filter(is_available=True).order_by('-posted_at')
    
    # Get user's requests
    user_requests = FoodRequest.objects.filter(requester=request.user).order_by('-requested_at')
    
    # Get collaborations
    collaborations = Collaboration.objects.filter(ngo=request.user).order_by('-collaboration_date')
    active_collaborations = Collaboration.objects.filter(ngo=request.user, status='ACTIVE').order_by('-collaboration_date')
    
    # Get analysis data
    analysis, created = Analysis.objects.get_or_create(user=request.user)
    
    # Recalculate monthly people served and get badge level
    analysis.recalculate_monthly_people_served()
    badge_level = analysis.get_badge_level()
    analysis.badge_level = badge_level
    analysis.save()
    
    # Get all restaurants with their updated profile information (always fetch fresh data)
    all_restaurants = []
    restaurant_users = User.objects.filter(role=User.Role.RESTAURANT)
    
    for restaurant_user in restaurant_users:
        
        try:
            restaurant_profile = RestaurantProfile.objects.get(user=restaurant_user)
            all_restaurants.append({
                'user': restaurant_user,
                'profile': restaurant_profile
            })
        except RestaurantProfile.DoesNotExist:
            # Fallback to old UserProfile if RestaurantProfile doesn't exist
            try:
                from core.models import UserProfile
                old_profile = UserProfile.objects.get(user=restaurant_user)
                all_restaurants.append({
                    'user': restaurant_user,
                    'profile': old_profile
                })
            except:
                # If no profile exists, create a minimal one
                all_restaurants.append({
                    'user': restaurant_user,
                    'profile': None
                })
    
    context = {
        'all_food_donations': all_food_donations,
        'user_requests': user_requests,
        'collaborations': collaborations,
        'active_collaborations': active_collaborations,
        'analysis': analysis,
        'badge_level': badge_level,
        'all_restaurants': all_restaurants,
    }
    return render(request, 'dashboards/ngo_dashboard.html', context)

@login_required
def add_food_request(request):
    if request.method == 'POST':
        form = FoodRequestForm(request.POST)
        if form.is_valid():
            food_request = form.save(commit=False)
            food_request.requester = request.user
            food_request.save()
            messages.success(request, 'Food request added successfully!')
            return redirect('ngo_dashboard')
    else:
        form = FoodRequestForm()
    
    return render(request, 'ngo/add_food_request.html', {'form': form})

@login_required
def edit_food_request(request, request_id):
    food_request = get_object_or_404(FoodRequest, id=request_id, requester=request.user)
    if request.method == 'POST':
        form = FoodRequestForm(request.POST, instance=food_request)
        if form.is_valid():
            form.save()
            messages.success(request, 'Food request updated successfully!')
            return redirect('ngo_dashboard')
    else:
        form = FoodRequestForm(instance=food_request)
    
    return render(request, 'ngo/edit_food_request.html', {'form': form, 'food_request': food_request})

@login_required
def delete_food_request(request, request_id):
    food_request = get_object_or_404(FoodRequest, id=request_id, requester=request.user)
    if request.method == 'POST':
        food_request.delete()
        messages.success(request, 'Food request deleted successfully!')
        return redirect('ngo_dashboard')
    
    return render(request, 'ngo/delete_food_request.html', {'food_request': food_request})

@login_required
def request_food_from_donation(request, donation_id):
    donation = get_object_or_404(FoodDonation, id=donation_id)
    if request.method == 'POST':
        form = CollaborationForm(request.POST)
        if form.is_valid():
            collaboration = form.save(commit=False)
            collaboration.donor = donation.donor
            collaboration.ngo = request.user
            collaboration.food_donation = donation
            collaboration.status = 'PENDING'
            collaboration.save()
            
            messages.success(request, 'Request sent successfully!')
            return redirect('ngo_dashboard')
    else:
        form = CollaborationForm()
    
    return render(request, 'ngo/request_food_from_donation.html', {
        'form': form, 
        'donation': donation
    })

@login_required
def view_restaurant_details(request, restaurant_id):
    restaurant = get_object_or_404(User, id=restaurant_id, role=User.Role.RESTAURANT)
    restaurant_donations = FoodDonation.objects.filter(donor=restaurant, is_available=True)
    collaborations = Collaboration.objects.filter(
        Q(donor=restaurant, ngo=request.user) | Q(donor=request.user, ngo=restaurant)
    )
    
    # Get restaurant profile information
    try:
        restaurant_profile = RestaurantProfile.objects.get(user=restaurant)
    except RestaurantProfile.DoesNotExist:
        # Fallback to old UserProfile if RestaurantProfile doesn't exist
        try:
            from core.models import UserProfile
            restaurant_profile = UserProfile.objects.get(user=restaurant)
        except:
            restaurant_profile = None
    
    return render(request, 'ngo/restaurant_details.html', {
        'restaurant': restaurant,
        'restaurant_profile': restaurant_profile,
        'restaurant_donations': restaurant_donations,
        'collaborations': collaborations
    })

@login_required
def ngo_profile(request):
    profile, created = NGOProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = NGOProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('ngo_dashboard')
    else:
        form = NGOProfileForm(instance=profile)
    
    return render(request, 'ngo/profile.html', {'form': form, 'profile': profile})

@login_required
def view_all_donations(request):
    """View all food donations in a separate page"""
    all_food_donations = FoodDonation.objects.filter(is_available=True).order_by('-posted_at')
    return render(request, 'ngo/view_all_donations.html', {'all_food_donations': all_food_donations})

@login_required
def view_all_restaurants(request):
    """View all restaurants in a separate page"""
    # Get all restaurants with their updated profile information
    all_restaurants = []
    restaurant_users = User.objects.filter(role=User.Role.RESTAURANT)
    for restaurant_user in restaurant_users:
        try:
            restaurant_profile = RestaurantProfile.objects.get(user=restaurant_user)
            all_restaurants.append({
                'user': restaurant_user,
                'profile': restaurant_profile
            })
        except RestaurantProfile.DoesNotExist:
            # Fallback to old UserProfile if RestaurantProfile doesn't exist
            try:
                from core.models import UserProfile
                old_profile = UserProfile.objects.get(user=restaurant_user)
                all_restaurants.append({
                    'user': restaurant_user,
                    'profile': old_profile
                })
            except:
                # If no profile exists, create a minimal one
                all_restaurants.append({
                    'user': restaurant_user,
                    'profile': None
                })
    
    return render(request, 'ngo/view_all_restaurants.html', {'all_restaurants': all_restaurants})

@login_required
def view_all_eventplanners(request):
    """View all event planners in a separate page"""
    # Get all event planners with their updated profile information
    all_eventplanners = []
    eventplanner_users = User.objects.filter(role=User.Role.EVENTPLANNER)
    for eventplanner_user in eventplanner_users:
        try:
            eventplanner_profile = EventPlannerProfile.objects.get(user=eventplanner_user)
            all_eventplanners.append({
                'user': eventplanner_user,
                'profile': eventplanner_profile
            })
        except EventPlannerProfile.DoesNotExist:
            # Fallback to old UserProfile if EventPlannerProfile doesn't exist
            try:
                from core.models import UserProfile
                old_profile = UserProfile.objects.get(user=eventplanner_user)
                all_eventplanners.append({
                    'user': eventplanner_user,
                    'profile': old_profile
                })
            except:
                # If no profile exists, create a minimal one
                all_eventplanners.append({
                    'user': eventplanner_user,
                    'profile': None
                })
    
    return render(request, 'ngo/view_all_eventplanners.html', {'all_eventplanners': all_eventplanners})

@login_required
def complete_donation(request, collaboration_id):
    """Complete a donation by NGO - mark as completed and record people served"""
    collaboration = get_object_or_404(Collaboration, id=collaboration_id, ngo=request.user, status='ACTIVE')
    
    if request.method == 'POST':
        form = CollaborationCompletionForm(request.POST, instance=collaboration)
        if form.is_valid():
            collaboration = form.save(commit=False)
            collaboration.status = 'COMPLETED'
            from django.utils import timezone
            collaboration.completion_date = timezone.now()
            collaboration.save()
            
            # Update analysis counts
            try:
                donor_analysis, created = Analysis.objects.get_or_create(user=collaboration.donor)
                donor_analysis.ngos_helped_count += 1
                donor_analysis.collaborations_count += 1
                donor_analysis.save()
                
                ngo_analysis, created = Analysis.objects.get_or_create(user=collaboration.ngo)
                ngo_analysis.requests_fulfilled_count += 1
                ngo_analysis.total_people_served += collaboration.people_served
                ngo_analysis.save()
            except:
                pass  # Don't fail if analysis update fails
            
            messages.success(request, f'Donation completed! You served {collaboration.people_served} people.')
            return redirect('ngo_dashboard')
    else:
        form = CollaborationCompletionForm(instance=collaboration)
    
    return render(request, 'ngo/complete_donation.html', {
        'form': form,
        'collaboration': collaboration
    })

def ngo_badge_info(request):
    """Displays badge information for NGOs."""
    return render(request, 'badges/ngo_badge_info.html')
