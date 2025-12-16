from django.shortcuts import render
from rest_framework import generics, permissions
from .models import Post
from .serializers import PostSerializer
from rest_framework.permissions import IsAuthenticated
from .permissions import IsAuthorOrReadOnly

# Create your views here.
#View for listing all posts and creating new posts
class PostListCreateView(generics.ListCreateAPIView):
  queryset = Post.objects.all().order_by('-created_at') #Oder by newest first
  serializer_class = PostSerializer
  
  #Only Authenticated users can CREATE posts
  def get_permissions(self):
    if self.request.method == 'POST':
      #Require authentication for the POST (Creation)
      return [IsAuthenticated]
    #Allow anyone to view the list (GET)
    return [permissions.AllowAny()]
  
  def perform_create(self, serializer):
    #Called right before post object is saved, sets the author to the logged-in User
    serializer.save(author=self.request.user)

#View for retrieving a single post (Read) and updating/deleting 
class PostDetailView(generics.RetrieveUpdateDestroyAPIView):
  queryset = Post.objects.all()
  serializer_class = PostSerializer
  
  # 1. User must be logged in (IsAuthenticated) to attempt modification.
  # 2. They must pass the custom check (IsAuthorOrReadOnly).
  permission_classes = [IsAuthenticated, IsAuthorOrReadOnly]