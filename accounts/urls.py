from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('delete-account/', views.delete_account, name='delete_account'),
    path('debug-csrf/', views.debug_csrf, name='debug_csrf'),
] 