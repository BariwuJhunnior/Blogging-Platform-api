from rest_framework import serializers
from django.contrib.auth.models import User
from posts.serializers import PostSerializer
from .models import Profile

class UserRegistrationSerializer(serializers.ModelSerializer):
  password = serializers.CharField(write_only=True)

  class Meta:
    model = User
    fields = ['id', 'username', 'email', 'password']

  
  def create(self, validated_data):
    user = User.objects.create_user(
      username=validated_data['username'],
      email=validated_data['email'],
      password=validated_data['password']
    )

    return user

class UserProfileSerializer(serializers.ModelSerializer):
  class Meta:
    model = User

    fields = ('id', 'username', 'email', 'first_name', 'last_name')
    read_only_fields = ('username',)

class ProfileSerializer(serializers.ModelSerializer):
  username = serializers.ReadOnlyField(source='user.username')
  #Include the user's posts directly in the profile
  posts = serializers.SerializerMethodField()


  class Meta:
    model = Profile
    fields = ['username', 'bio', 'profile_picture', 'location', 'posts']

  def get_posts(self, obj):
    #Obj is the Profile instance
    user_posts = obj.user.posts.filter(status='PB')
    return PostSerializer(user_posts, many=True).data
  
class UserSerializer(serializers.ModelSerializer):
  #Include the profile bio we created earlier
  bio = serializers.CharField(source='profile.bio', read_only=True)

  class Meta:
    model = User
    fields = ['id', 'username', 'email', 'bio']