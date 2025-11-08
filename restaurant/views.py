from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model
from core.models import FoodDonation, FoodRequest, Collaboration, Analysis, RestaurantProfile, NGOProfile, EventPlannerProfile
from core.forms import FoodDonationForm, CollaborationForm, RestaurantProfileForm
from django.db.models import Count, Q
from datetime import datetime, timedelta

User = get_user_model()

def calculate_user_tier(user):
    """
    Calculate user tier based on donation frequency:
    - GOLD: Donates every 48 hours (2 days)
    - PLATINUM: Donates once every week (7 days)
    - SILVER: Donates once every 15 days
    - No tier: Doesn't donate more than 15 days
    """
    now = datetime.now()
    
    # Get all donations by the user
    donations = FoodDonation.objects.filter(donor=user).order_by('-posted_at')
    
    if not donations.exists():
        return None, "No donations yet"
    
    # Get the most recent donation
    last_donation = donations.first()
    days_since_last = (now - last_donation.posted_at.replace(tzinfo=None)).days
    
    # Check if user has been consistently donating
    if donations.count() < 2:
        # Need at least 2 donations to determine pattern
        if days_since_last <= 2:
            return "GOLD", "Gold Tier - Recent donor!"
        elif days_since_last <= 7:
            return "PLATINUM", "Platinum Tier - Weekly donor!"
        elif days_since_last <= 15:
            return "SILVER", "Silver Tier - Bi-weekly donor!"
        else:
            return None, "No active tier"
    
    # Calculate average donation frequency
    donation_dates = [d.posted_at for d in donations[:10]]  # Last 10 donations
    if len(donation_dates) < 2:
        return None, "Need more donation history"
    
    # Calculate average days between donations
    total_days = 0
    for i in range(len(donation_dates) - 1):
        days_diff = (donation_dates[i] - donation_dates[i + 1]).days
        total_days += days_diff
    
    avg_days_between = total_days / (len(donation_dates) - 1)
    
    # Determine tier based on frequency and recency
    if avg_days_between <= 2 and days_since_last <= 2:
        return "GOLD", "Gold Tier - Donates every 2 days!"
    elif avg_days_between <= 7 and days_since_last <= 7:
        return "PLATINUM", "Platinum Tier - Weekly donor!"
    elif avg_days_between <= 15 and days_since_last <= 15:
        return "SILVER", "Silver Tier - Bi-weekly donor!"
    else:
        return None, "No active tier"

@login_required
def restaurant_dashboard(request):
    # Get user's donations (always fetch fresh data)
    user_donations = FoodDonation.objects.filter(donor=request.user, is_available=True).order_by('-posted_at')
    total_donations = FoodDonation.objects.filter(donor=request.user).count()
    
    # Get pending requests from NGOs (always fetch fresh data)
    ngo_requests = FoodRequest.objects.filter(status='PENDING').order_by('-requested_at')
    
    # Get collaborations
    collaborations = Collaboration.objects.filter(donor=request.user).order_by('-collaboration_date')
    pending_donation_requests = Collaboration.objects.filter(donor=request.user, status='PENDING', food_donation__isnull=False).order_by('-collaboration_date')
    completed_collaborations = Collaboration.objects.filter(donor=request.user, status='COMPLETED').order_by('-completion_date')
    
    # Get analysis data
    analysis, created = Analysis.objects.get_or_create(user=request.user)
    
    # Recalculate monthly donations made and get badge level
    analysis.recalculate_monthly_donations_made()
    badge_level = analysis.get_badge_level()
    analysis.badge_level = badge_level
    analysis.save()
    
    # Get all NGOs with their updated profile information (always fetch fresh data)
    all_ngos = []
    ngo_users = User.objects.filter(role=User.Role.NGO)
    for ngo_user in ngo_users:
        try:
            ngo_profile = NGOProfile.objects.get(user=ngo_user)
            all_ngos.append({
                'user': ngo_user,
                'profile': ngo_profile
            })
        except NGOProfile.DoesNotExist:
            # Fallback to old UserProfile if NGOProfile doesn't exist
            try:
                from core.models import UserProfile
                old_profile = UserProfile.objects.get(user=ngo_user)
                all_ngos.append({
                    'user': ngo_user,
                    'profile': old_profile
                })
            except:
                # If no profile exists, create a minimal one
                all_ngos.append({
                    'user': ngo_user,
                    'profile': None
                })
    
    context = {
        'user_donations': user_donations,
        'total_donations': total_donations,
        'ngo_requests': ngo_requests,
        'collaborations': collaborations,
        'analysis': analysis,
        'badge_level': badge_level,
        'pending_donation_requests': pending_donation_requests,
        'completed_collaborations': completed_collaborations,
        'all_ngos': all_ngos,
    }
    return render(request, 'dashboards/restaurant_dashboard.html', context)

@login_required
def add_food_donation(request):
    if request.method == 'POST':
        form = FoodDonationForm(request.POST, request.FILES)
        if form.is_valid():
            donation = form.save(commit=False)
            donation.donor = request.user
            donation.save()
            messages.success(request, 'Food donation added successfully!')
            return redirect('restaurant_dashboard')
    else:
        form = FoodDonationForm()
    
    return render(request, 'restaurant/add_food_donation.html', {'form': form})

@login_required
def update_food_donation(request, donation_id):
    donation = get_object_or_404(FoodDonation, id=donation_id, donor=request.user)
    if request.method == 'POST':
        form = FoodDonationForm(request.POST, request.FILES, instance=donation)
        if form.is_valid():
            form.save()
            messages.success(request, 'Food donation updated successfully!')
            return redirect('restaurant_dashboard')
    else:
        form = FoodDonationForm(instance=donation)
    
    return render(request, 'restaurant/update_food_donation.html', {'form': form, 'donation': donation})

@login_required
def remove_food_donation(request, donation_id):
    donation = get_object_or_404(FoodDonation, id=donation_id, donor=request.user)
    if request.method == 'POST':
        donation.delete()
        messages.success(request, 'Food donation removed successfully!')
        return redirect('restaurant_dashboard')
    
    return render(request, 'restaurant/remove_food_donation.html', {'donation': donation})

@login_required
def fulfill_ngo_request(request, request_id):
    ngo_request = get_object_or_404(FoodRequest, id=request_id)
    if request.method == 'POST':
        form = CollaborationForm(request.POST)
        if form.is_valid():
            collaboration = form.save(commit=False)
            collaboration.donor = request.user
            collaboration.ngo = ngo_request.requester
            collaboration.food_request = ngo_request
            collaboration.status = 'ACTIVE'
            collaboration.save()
            
            # Update request status
            ngo_request.status = 'ACCEPTED'
            ngo_request.save()
            
            messages.success(request, 'Request fulfilled successfully!')
            return redirect('restaurant_dashboard')
    else:
        form = CollaborationForm()
    
    return render(request, 'restaurant/fulfill_ngo_request.html', {
        'form': form, 
        'ngo_request': ngo_request
    })

@login_required
def view_ngo_details(request, ngo_id):
    ngo = get_object_or_404(User, id=ngo_id, role=User.Role.NGO)
    ngo_requests = FoodRequest.objects.filter(requester=ngo)
    collaborations = Collaboration.objects.filter(
        Q(donor=request.user, ngo=ngo) | Q(donor=ngo, ngo=request.user)
    )
    
    # Get NGO profile information
    try:
        ngo_profile = NGOProfile.objects.get(user=ngo)
    except NGOProfile.DoesNotExist:
        # Fallback to old UserProfile if NGOProfile doesn't exist
        try:
            from core.models import UserProfile
            ngo_profile = UserProfile.objects.get(user=ngo)
        except:
            ngo_profile = None
    
    return render(request, 'restaurant/ngo_details.html', {
        'ngo': ngo,
        'ngo_profile': ngo_profile,
        'ngo_requests': ngo_requests,
        'collaborations': collaborations
    })

@login_required
def restaurant_profile(request):
    profile, created = RestaurantProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = RestaurantProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('restaurant_dashboard')
    else:
        form = RestaurantProfileForm(instance=profile)
    
    return render(request, 'restaurant/profile.html', {'form': form, 'profile': profile})

@login_required
def view_all_requests(request):
    """View all NGO requests in a separate page"""
    ngo_requests = FoodRequest.objects.filter(status='PENDING').order_by('-requested_at')
    return render(request, 'restaurant/view_all_requests.html', {'ngo_requests': ngo_requests})

@login_required
def accept_donation_request(request, collaboration_id):
    collaboration = get_object_or_404(Collaboration, id=collaboration_id, donor=request.user)
    if request.method == 'POST':
        collaboration.status = 'ACTIVE'
        collaboration.save()
        # mark the donation as no longer available
        if collaboration.food_donation:
            collaboration.food_donation.is_available = False
            collaboration.food_donation.is_accepted = True
            collaboration.food_donation.save()
        messages.success(request, 'Donation request accepted.')
        return redirect('restaurant_dashboard')
    return redirect('restaurant_dashboard')

@login_required
def reject_donation_request(request, collaboration_id):
    collaboration = get_object_or_404(Collaboration, id=collaboration_id, donor=request.user)
    if request.method == 'POST':
        collaboration.status = 'CANCELLED'
        collaboration.save()
        messages.success(request, 'Donation request rejected.')
        return redirect('restaurant_dashboard')
    return redirect('restaurant_dashboard')

@login_required
def view_all_ngos(request):
    """View all NGOs in a separate page"""
    # Get all NGOs with their updated profile information
    all_ngos = []
    ngo_users = User.objects.filter(role=User.Role.NGO)
    for ngo_user in ngo_users:
        try:
            ngo_profile = NGOProfile.objects.get(user=ngo_user)
            all_ngos.append({
                'user': ngo_user,
                'profile': ngo_profile
            })
        except NGOProfile.DoesNotExist:
            # Fallback to old UserProfile if NGOProfile doesn't exist
            try:
                from core.models import UserProfile
                old_profile = UserProfile.objects.get(user=ngo_user)
                all_ngos.append({
                    'user': ngo_user,
                    'profile': old_profile
                })
            except:
                # If no profile exists, create a minimal one
                all_ngos.append({
                    'user': ngo_user,
                    'profile': None
                })
    
    return render(request, 'restaurant/view_all_ngos.html', {'all_ngos': all_ngos})

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
    
    return render(request, 'restaurant/view_all_eventplanners.html', {'all_eventplanners': all_eventplanners})

def donor_badge_info(request):
    """Displays badge information for donors (Restaurants and Event Planners)."""
    return render(request, 'badges/donor_badge_info.html')
