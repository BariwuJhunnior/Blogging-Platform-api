from django.shortcuts import render
from rest_framework import generics, permissions
from .serializers import UserRegistrationSerializer
from django.contrib.auth.models import User
from rest_framework.permissions import IsAuthenticated
from .serializers import UserProfileSerializer, ProfileSerializer, UserSerializer
from .models import Profile
from django.core import exceptions



# Create your views here.
class RegisterView(generics.CreateAPIView):
  queryset = User.objects.all()

  permission_classes = [permissions.AllowAny]
  serializer_class = UserRegistrationSerializer


class UserProfileView(generics.RetrieveUpdateAPIView):
  serializer_class = UserProfileSerializer
  # This ensures only logged-in users can access this endpoint
  permission_classes = [IsAuthenticated]

  # Override get_object to ensure users can only access their OWN profile
  def get_object(self):
    # The request.user is automatically set by the TokenAuthentication 
    # middleware if the user is logged in.
    return self.request.user
  
class ProfileDetailView(generics.RetrieveUpdateAPIView):
  queryset = Profile.objects.all()
  serializer_class = ProfileSerializer
  lookup_field = 'user__username' #Search by /profile/john/instead of /profile/1/

  def get_permissions(self):
    if self.request.method in permissions.SAFE_METHODS:
      return [permissions.AllowAny()]
    return [permissions.IsAuthenticated()]
  
  def perform_update(self, serializer):
    #Ensure a user can only update their own profile
    if serializer.instance.user != self.request.user:
      raise exceptions.PermissionDenied("You cannot edit someone else's profile.")
    serializer.save()

class UserListView(generics.ListAPIView):
  queryset = User.objects.all()
  serializer_class = UserSerializer
  permission_classes = [permissions.AllowAny] #Anyone can see the author list