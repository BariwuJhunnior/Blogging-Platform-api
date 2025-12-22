from django.shortcuts import render
from rest_framework import generics, permissions
from .models import Post
from .serializers import PostSerializer
from rest_framework.permissions import IsAuthenticated
from .permissions import IsAuthorOrReadOnly
from .filters import PostFilter
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import generics

@extend_schema_view(
  list=extend_schema(summary="List all posts"),
  create=extend_schema(summary="Create a post"),
  
)
# Create your views here.
#View for listing all posts and creating new posts
class PostListCreateView(generics.ListCreateAPIView):
  queryset = Post.objects.all().order_by('-created_at') #Order by newest first
  serializer_class = PostSerializer
  filterset_class = PostFilter

  filter_backends = [
    DjangoFilterBackend,
    filters.SearchFilter
  ]

  search_fields = ['title', 'content', 'author__username', 'tags__name']
  
  #Only Authenticated users can CREATE posts
  def get_permissions(self):
    if self.request.method == 'POST':
      #Require authentication for the POST (Creation)
      return [IsAuthenticated()]
    #Allow anyone to view the list (GET)
    return [permissions.AllowAny()]
  
  def perform_create(self, serializer):
    #Called right before post object is saved, sets the author to the logged-in User
    serializer.save(author=self.request.user)

@extend_schema_view(
  retrieve=extend_schema(summary="Get post details"),
  update=extend_schema(summary="Full update of post"),
  partial_update=extend_schema(summary="Partial update of post"),
  destroy=extend_schema(summary="Delete a post"),
)
#View for retrieving a single post (Read) and updating/deleting 
class PostDetailView(generics.RetrieveUpdateDestroyAPIView):
  queryset = Post.objects.all().order_by('-created_at') #Order by newest first
  serializer_class = PostSerializer
  
  # 1. User must be logged in (IsAuthenticated) to attempt modification.
  # 2. They must pass the custom check (IsAuthorOrReadOnly).
  permission_classes = [IsAuthenticated, IsAuthorOrReadOnly]