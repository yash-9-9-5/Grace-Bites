from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.restaurant_dashboard, name='restaurant_dashboard'),
    path('add-food/', views.add_food_donation, name='add_food_donation'),
    path('update-food/<int:donation_id>/', views.update_food_donation, name='update_food_donation'),
    path('remove-food/<int:donation_id>/', views.remove_food_donation, name='remove_food_donation'),
    path('fulfill-request/<int:request_id>/', views.fulfill_ngo_request, name='fulfill_ngo_request'),
    path('ngo-details/<int:ngo_id>/', views.view_ngo_details, name='view_ngo_details'),
    path('profile/', views.restaurant_profile, name='restaurant_profile'),
    path('view-all-requests/', views.view_all_requests, name='view_all_requests'),
    path('view-all-ngos/', views.view_all_ngos, name='view_all_ngos'),
    path('view-all-eventplanners/', views.view_all_eventplanners, name='view_all_eventplanners'),
    path('donation-request/<int:collaboration_id>/accept/', views.accept_donation_request, name='accept_donation_request'),
    path('donation-request/<int:collaboration_id>/reject/', views.reject_donation_request, name='reject_donation_request'),
    path('badge-info/donor/', views.donor_badge_info, name='donor_badge_info'),
]