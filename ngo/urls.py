from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.ngo_dashboard, name='ngo_dashboard'),
    path('add-request/', views.add_food_request, name='add_food_request'),
    path('edit-request/<int:request_id>/', views.edit_food_request, name='edit_food_request'),
    path('delete-request/<int:request_id>/', views.delete_food_request, name='delete_food_request'),
    path('request-food/<int:donation_id>/', views.request_food_from_donation, name='request_food_from_donation'),
    path('restaurant-details/<int:restaurant_id>/', views.view_restaurant_details, name='view_restaurant_details'),
    path('profile/', views.ngo_profile, name='ngo_profile'),
    path('view-all-donations/', views.view_all_donations, name='view_all_donations'),
    path('view-all-restaurants/', views.view_all_restaurants, name='view_all_restaurants'),
    path('view-all-eventplanners/', views.view_all_eventplanners, name='view_all_eventplanners'),
    path('complete-donation/<int:collaboration_id>/', views.complete_donation, name='complete_donation'),
    path('badge-info/ngo/', views.ngo_badge_info, name='ngo_badge_info'),
]