from django.urls import path
from django.contrib.auth import views as auth_views #Django's built-in views
from . import views

urlpatterns = [
    # Custom Registration and Profile views
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),

    # Built-in Login View
    path('login/', auth_views.LoginView.as_view(template_name='blog/login.html'), name='login'),

    # Built-in Logout View
    path('logout/', auth_views.LogoutView.as_view(template_name='blog/logout.html'), name='logout'),
]
