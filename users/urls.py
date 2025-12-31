from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from .views import RegisterView, UserProfileView, ProfileDetailView, UserListView, FollowUserView


urlpatterns = [
    path("register/", RegisterView.as_view(), name='register'),
    path('login/', obtain_auth_token, name='api-token-auth'),
    path('profile/', UserProfileView.as_view(), name='user-profile'),
    #Profile endpoint using the username as a lookup
    path('profiles/<str:username>/', ProfileDetailView.as_view(), name='profile-detail'),
    path('profiles/<str:username>/follow/', FollowUserView.as_view(), name='user-follow'),
    path('users/', UserListView.as_view(), name='user-list'),
]
