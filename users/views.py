from django.shortcuts import render
from rest_framework import generics, permissions, serializers
from rest_framework.response import Response
from .serializers import UserRegistrationSerializer
from django.contrib.auth.models import User
from rest_framework.permissions import IsAuthenticated
from .serializers import UserProfileSerializer, ProfileSerializer, UserSerializer
from .models import Profile, Follow
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

  lookup_field = 'user__username'
  lookup_url_kwarg = 'username'

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


class EmptySerializer(serializers.Serializer):
    pass

class FollowUserView(generics.GenericAPIView):
  permission_classes = [IsAuthenticated]
  serializer_class = EmptySerializer

  def post(self, request, username):
    target_user = generics.get_object_or_404(User, username=username)
    if target_user == request.user:
      return Response({"error": "You cannot follow yourself."}, status=400)
    
    follow, created = Follow.objects.get_or_create(follower=request.user, author=target_user)

    if not created:
      follow.delete()
      return Response({"message": f"Unfollowed {username}"})
    
    return Response({"message": f"Following {username}"}, status=201)
  
