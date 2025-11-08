from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.eventplanner_dashboard, name='eventplanner_dashboard'),
    path('add-event-food/', views.add_event_food_donation, name='add_event_food_donation'),
    path('update-event-food/<int:donation_id>/', views.update_event_food_donation, name='update_event_food_donation'),
    path('remove-event-food/<int:donation_id>/', views.remove_event_food_donation, name='remove_event_food_donation'),
    path('fulfill-request-from-event/<int:request_id>/', views.fulfill_ngo_request_from_event, name='fulfill_ngo_request_from_event'),
    path('ngo-details-from-event/<int:ngo_id>/', views.view_ngo_details_from_event, name='view_ngo_details_from_event'),
    path('profile/', views.eventplanner_profile, name='eventplanner_profile'),
    path('view-all-requests/', views.view_all_requests_from_event, name='view_all_requests_from_event'),
    path('view-all-ngos/', views.view_all_ngos_from_event, name='view_all_ngos_from_event'),
    path('donation-request/<int:collaboration_id>/accept/', views.accept_event_donation_request, name='accept_event_donation_request'),
    path('donation-request/<int:collaboration_id>/reject/', views.reject_event_donation_request, name='reject_event_donation_request'),
] 