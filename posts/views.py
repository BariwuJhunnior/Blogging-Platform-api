from django.shortcuts import render, get_object_or_404
from rest_framework import generics, permissions, status
from .models import Post, Comment, Like, Rating
from .serializers import PostSerializer, CommentSerializer
from rest_framework.permissions import IsAuthenticated
from .permissions import IsAuthorOrReadOnly
from .filters import PostFilter
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiResponse, inline_serializer, OpenApiParameter
from rest_framework import generics
from rest_framework import serializers
from django.db.models import Count, Avg, QuerySet
from django.db.models.functions import Coalesce
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Q
from rest_framework.decorators import action
from .tasks import share_post_via_email
from .utils import get_social_share_links

#A simple serializer for one-off messages
MessageSerializer = inline_serializer(
  name='MessageResponse',
  fields={
    'message': serializers.CharField()
  }
)

#View for listing all posts and creating new posts
#API documentation with drf-spectacular
@extend_schema_view(
  list=extend_schema(
    summary='List all posts.',
    responses={
      201: PostSerializer, #Succesful Creation
      400: OpenApiResponse(description='Bad Request - Invalid data provided.'),
      401: OpenApiResponse(description='Unauthorized - Token is missing or invalid'),
    },
    description='Retrieve a list of blog posts with support for search and category filtering',
    tags=['Public Feed']
  ),
  create=extend_schema(
    summary='Create a blog post.',
    description='Authorized users can create posts. Author is set automatically.',
    tags=['Author Actions']
  ),
)
class PostListCreateView(generics.ListCreateAPIView):
  
  serializer_class = PostSerializer
  filterset_class = PostFilter

  filter_backends = [
    DjangoFilterBackend,
    filters.SearchFilter
  ]

  search_fields = ['title', 'content', 'author__username', 'tags__name']

  def get_queryset(self): # type: ignore
    user = self.request.user
    queryset = Post.objects.select_related('author', 'category').prefetch_related('tags', 'likes', 'ratings').all().order_by('-created_at)') #Order by newest osts

    if user.is_authenticated:
      #Show all published posts OR dragts owned by the current user
      return queryset.filter(
        Q(status=Post.Status.PUBLISHED) | Q(author=user)
      )
    
    #Anonymous users only see published posts
    return queryset.filter(status=Post.Status.PUBLISHED)
  
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
  update=extend_schema(
    summary='Update a post',
    responses={
      200: PostSerializer,
      403: OpenApiResponse(
        description='Forbidden - You are not the author of this post',
        response=MessageSerializer
      ),
      404: OpenApiResponse(description='Not Found - Post ID does not exits')
    }
  ),
  destroy=extend_schema(
    summary='Delete a post',
    responses={
      204: OpenApiResponse(description='No Content - Successfully deleted'),
      403: OpenApiResponse(description='Forbidden - Only authors can delete.')
    }
  )
)
#View for retrieving a single post (Read) and updating/deleting 
class PostDetailView(generics.RetrieveUpdateDestroyAPIView):
  queryset = Post.objects.all().order_by('-created_at') #Order by newest first
  serializer_class = PostSerializer
  
  # 1. User must be logged in (IsAuthenticated) to attempt modification.
  # 2. They must pass the custom check (IsAuthorOrReadOnly).
  permission_classes = [IsAuthenticated, IsAuthorOrReadOnly]

@extend_schema_view(
  list=extend_schema(summary='List comments for a post', tags=['Comments']),
  create=extend_schema(summary='Add a comment to a post', tags=['Comments']),
)
class CommentListCreateView(generics.ListCreateAPIView):
  serializer_class = CommentSerializer
  permission_classes = [permissions.IsAuthenticatedOrReadOnly]

  def get_queryset(self) -> QuerySet[Comment]:  # type: ignore [override]
    #Only return comments for the post specified in the URL
    return Comment.objects.filter(post_id=self.kwargs['post_pk']).order_by('-created_at')
  
  def perform_create(self, serializer):
    # Automatically assign author and post
    post = get_object_or_404(Post, pk=self.kwargs['post_pk'])
    serializer.save(author=self.request.user, post=post)

@extend_schema_view(
  update=extend_schema(summary='Edit a comment', tags=['Comments']),
  destroy=extend_schema(summary='Delete a comment', tags=['Comments']),
)
class CommentDetailView(generics.RetrieveUpdateDestroyAPIView):
  queryset = Comment.objects.all().order_by('-created_at')
  serializer_class = CommentSerializer
  permission_classes = [IsAuthorOrReadOnly] #Reusing our custom permissions

class TopPostsView(generics.ListAPIView):
  """
  Returns the top posts based on likes or average rating.
  """
  serializer_class = PostSerializer

  @extend_schema(
    summary='Get top rated/liked posts', 
    parameters=[
      OpenApiParameter(name='sort_by', type=str, description='Sort by "likes" or "rating"')
    ]
  )
  def get_queryset(self) -> QuerySet[Post]:  # type: ignore [override]
    queryset = Post.objects.annotate(
      likes_count = Count('likes'),
      avg_rating=Coalesce(Avg('ratings__score'), 0)
    )

    sort_by = self.request.GET.get('sort_by', 'likes')
    if sort_by == 'rating':
      return queryset.order_by('-avg_rating')
    return queryset.order_by('-likes_count')
    
class LikePostView(APIView):
  permission_classes = [permissions.IsAuthenticated]

  @extend_schema(summary='Toggle like on a post', responses={200: OpenApiResponse(description='Success')})
  def post(self, request, pk):
    post = generics.get_object_or_404(Post, pk=pk)
    like, created = Like.objects.get_or_create(user=request.user, post=post)

    if not created:
      like.delete()
      return Response({'message': 'Unliked'}, status=status.HTTP_200_OK)

    return Response({'message': 'Liked'}, status=status.HTTP_201_CREATED)
  
class RatePostView(generics.CreateAPIView):
  """
  Allows a user to submit a rating (1-5). Updates if already exists.
  """
  permission_classes = [permissions.IsAuthenticated]

  def post(self, request, pk):
    score = request.data.get('score')
    post = generics.get_object_or_404(Post, pk=pk)
    rating, created = Rating.objects.update_or_create(
      user=request.user, post=post, defaults={'score': score}
    )
    return Response({'message': 'Rating saved', 'score': score})
  
class PostPublishView(APIView):
  permission_classes = [IsAuthorOrReadOnly]

  @extend_schema(
    summary='Publish a draft post',
    responses={200: OpenApiResponse(description='Post is now live!')}
  )
  def post(self, request, pk):
    post = generics.get_object_or_404(Post, pk=pk)
    self.check_object_permissions(request, post)

    post.status = Post.Status.PUBLISHED
    post.save()

    return Response({'message': 'Post published successfully!'})
  
class PostShareView(APIView):
  permission_classes = [permissions.IsAuthenticatedOrReadOnly]

  @extend_schema(
    summary='Share a post',
    description="Trigger an email share and get social media links.",
    request=inline_serializer(
      name='ShareRequest',
      fields={'recipient_name': serializers.EmailField(), 'sender_name': serializers.CharField()}
    ),
    tags=['Social Actions']
  )
  def post(self, request, pk):
    post = generics.get_object_or_404(Post, pk=pk, status=Post.Status.PUBLISHED)

    #1. Define the Post URL (In production, use your actual domain)
    post_url = f"https:/myblog.com/posts/{post.id}/"

    #2. Trigger Async Email if email data is provided
    recipient = request.data.get('recipient_email')
    sender = request.data.get('sender_name', 'A friend')

    if recipient:
      share_post_via_email.delay(post.title, post_url, recipient, sender)

    #3. Return Social Links
    share_links = get_social_share_links(post_url, post.title)

    return Response({
      "message": "Email is being sent!" if recipient else "Social links generated.",
      "social_share_links": share_links
    }, status=status.HTTP_200_OK)