from rest_framework import serializers
from django.contrib.auth.models import User
from posts.serializers import PostSerializer
from .models import Profile
from drf_spectacular.utils import extend_schema_field

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
  posts = PostSerializer(source='user.posts', many=True, read_only=True)

  followers = serializers.SerializerMethodField()
  following = serializers.SerializerMethodField()

  followers_count = serializers.SerializerMethodField()
  following_count = serializers.SerializerMethodField()

  def get_followers_count(self, obj):
    return obj.user.followers.count()
  
  def get_following_count(self, obj):
    return obj.user.following.count()

  class Meta:
    model = Profile
    fields = ['id', 'username', 'bio', 'profile_picture', 'location', 'posts', 'followers_count', 'following_count', 'followers', 'following']

  @extend_schema_field(PostSerializer(many=True))
  def get_posts(self, obj):
    #Obj is the Profile instance
    published_posts = obj.user.posts.filter(status='PB')
    return PostSerializer(published_posts, many=True).data
  
class UserSerializer(serializers.ModelSerializer):
  #Include the profile bio we created earlier
  bio = serializers.CharField(source='profile.bio', read_only=True)

  class Meta:
    model = User
    fields = ['id', 'username', 'email', 'bio']