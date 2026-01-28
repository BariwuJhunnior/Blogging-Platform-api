from django.shortcuts import render, get_object_or_404
from rest_framework import generics, permissions, status
from .models import Post, Comment, Like, Rating, Category, CategorySubscription
from .serializers import PostSerializer, CommentSerializer, RatingSerializer, CategorySerializer
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
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
from rest_framework.decorators import action, api_view, permission_classes
from .tasks import share_post_via_email
from .utils import get_social_share_links
from django.utils import timezone

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
      201: PostSerializer, #Successful Creation
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

  def perform_create(self, serializer):
    serializer.save(author=self.request.user)

  def get_queryset(self): # type: ignore
    user = self.request.user
    queryset = Post.objects.select_related('author', 'category').prefetch_related('tags', 'likes', 'ratings').all().order_by('-created_at') #Order by newest posts

    if user.is_authenticated:
      #Show all published posts OR drafts owned by the current user
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
      404: OpenApiResponse(description='Not Found - Post ID does not exist')
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
  permission_classes = [IsAuthenticatedOrReadOnly]

  def get_serializer_context(self):
    context = super().get_serializer_context()
    context.update({"request": self.request})
    return context

@extend_schema_view(
  list=extend_schema(summary='List comments for a post', tags=['Comments']),
  create=extend_schema(summary='Add a comment to a post', tags=['Comments']),
)
class CommentListCreateView(generics.ListCreateAPIView):
  queryset = Comment.objects.none()
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
    
  
    return Post.objects.annotate(
      likes_count=Count('likes')
    ).order_by('-likes_count')[:10] #Get top 10
    
class LikePostView(APIView):
  permission_classes = [permissions.IsAuthenticated]
  serializer_class = None

  @extend_schema(summary='Toggle like on a post', responses={200: OpenApiResponse(description='Success')})
  def post(self, request, pk):
    post = get_object_or_404(Post, pk=pk)
    user = request.user

    if post.likes.filter(pk=user.pk).exists():
      post.likes.remove(user)
      message = "Post Unliked"
      status_code = status.HTTP_200_OK
    else:
      post.likes.add(user)
      message = "Post Liked"
      status_code = status.HTTP_201_CREATED

    return Response({
      "message": message,
      "current_total": post.likes.count(),
      "has_liked": post.likes.filter(pk=user.pk).exists()
    }, status=status_code)
  
class RatePostView(generics.CreateAPIView):
  """
  Allows a user to submit a rating (1-5). Updates if already exists.
  """
  permission_classes = [permissions.IsAuthenticated]
  serializer_class = RatingSerializer

  def post(self, request, pk):
    score = request.data.get('score')
    post = get_object_or_404(Post, pk=pk)
    rating, created = Rating.objects.update_or_create(
      user=request.user, post=post, defaults={'score': score}
    )
    return Response({'message': 'Rating saved', 'score': score})
  
class PostPublishView(APIView):
  permission_classes = [permissions.IsAuthenticated]

  @extend_schema(
    summary='Publish a draft post',
    responses={200: OpenApiResponse(description='Post is now live!')}
  )
  def post(self, request, pk):
    post = get_object_or_404(Post, pk=pk)
    
    if post.author != request.user:
      return Response({"error": "YOu are not the author"}, status=403)
    
    post.status = 'PB'
    post.save()
    return Response({"message": "Post published successfully!"})
  
class PostShareView(APIView):
  permission_classes = [permissions.IsAuthenticatedOrReadOnly]
  serializer_class = None

  @extend_schema(
    summary='Share a post',
    description="Trigger an email share and get social media links.",
    request=inline_serializer(
      name='ShareRequest',
      fields={'recipient_email': serializers.EmailField(), 'sender_name': serializers.CharField()}
    ),
    tags=['Social Actions']
  )
  def post(self, request, pk):
    post = get_object_or_404(Post, pk=pk, status=Post.Status.PUBLISHED)

    #1. Define the Post URL (In production, use your actual domain)
    post_url = f"https://myblog.com/posts/{post.id}/"

    #2. Trigger Async Email if email data is provided
    recipient = request.data.get('recipient_email')
    sender = request.data.get('sender_name', 'A friend')

    if recipient:
      share_post_via_email.delay(post.title, post_url, recipient, sender)  # type: ignore

    #3. Return Social Links
    share_links = get_social_share_links(post_url, post.title)

    return Response({
      "message": "Email is being sent!" if recipient else "Social links generated.",
      "social_share_links": share_links
    }, status=status.HTTP_200_OK)
   
class EmptySerializer(serializers.Serializer):
    pass

class SubscribeCategoryView(APIView):
  permission_classes = [IsAuthenticated]
  serializer_class = EmptySerializer

  @extend_schema(
    summary="Toggle category subscription",
    description="Subscribe to or unsubscribe from a specific category by its ID.",
    responses={
      200: OpenApiResponse(description="Unsubscrived successfully"),
      201: OpenApiResponse(description="Subscribed successfully"),
      404: OpenApiResponse(description="Category not found!")
    },
    tags=['Social Actions']
  )
  def post(self, request, category_id):
    #1. Verify if category exists
    category = generics.get_object_or_404(Category, id=category_id)
    #2. Toggle Logic: Try to get the subscription, create it if it doesn't exist
    subscription, created = CategorySubscription.objects.get_or_create(
      user=request.user,
      category=category
    )

    if not created:
      #If it already existed, the user wants to unsubscribe
      subscription.delete()
      return Response(
        {"message": f"Unsubscribed form {category.name}"},
        status=status.HTTP_200_OK
      )
    
    #If it was just created, the user is now subscribed
    return Response(
      {"message": f"Subscribed to {category.name}"},
      status=status.HTTP_201_CREATED
    )
  
class UserFeedView(generics.ListAPIView):
  serializer_class = PostSerializer
  permission_classes = [IsAuthenticated]

  @extend_schema(
    summary="Get personalized feed",
    description="Returns posts from authors you follow or categories you are subscribed to.",
    tags=['Social Actions']
  )
  def get_queryset(self) -> QuerySet[Post]:  # type: ignore [override]
    if getattr(self, 'swagger_fake_view', False):
        return Post.objects.none()

    user = self.request.user

    if user.is_superuser:
      return Post.objects.filter(status='PB').order_by('-published_at')

    #1. Get IDs of authors the user follows
    followed_authors = user.following.values_list('followed_user_id', flat=True)  # type: ignore

    #2. Get IDs of categories the user is subscribed to
    subscribed_categories = user.category_subscriptions.values_list('category_id', flat=True)  # type: ignore

    #3. Filter posts: (Author in list OR Category in list) AND Status is Published
    return Post.objects.filter(
      (Q(author_id__in=followed_authors) | Q(category_id__in=subscribed_categories)),
      status= Post.Status.PUBLISHED
    ).distinct().select_related('author', 'category').prefetch_related('tags').order_by('-published_at')


class GlobalFeedView(generics.ListAPIView):
  """
  Returns all published posts across the entire platform, 
  ordered by the most recently published.
  """
  serializer_class = PostSerializer
  permission_classes = [permissions.AllowAny] #Public, so new users can see content
  queryset = Post.objects.filter(status='PB').order_by('-published_at')

  #Filter Backends
  filter_backends = [filters.SearchFilter]

  #Fields that are searchable
  #Implement "Search": Add a search bar so users can find specific posts by keywords?
  search_fields = ['title', 'content', 'author__username', 'category__name']

  #1. Exact Filtering (Category name or Author username)
  filterset_fields = ['category__name', 'author__username']

  #2. Text Search (Partial matches)
  search_fields = ['title', 'content', 'tags__name']

  #3. Ordering (By date or by popularity)
  ordering_fields = ['published_at', 'likes_count']
  ordering = ['-published_at'] #Default ordering

  @extend_schema(
    summary="Get global discovery feed",
    description="Returns all published posts from all authors, newest first.",
    tags=['Discovery']
  )
  def get_queryset(self):

    queryset = Post.objects.filter(status='PB').order_by('-published_at')

    return Post.objects.filter(status=Post.Status.PUBLISHED).annotate(likes_count=Count('likes')).select_related('author', 'category').prefetch_related('tags')
  

@extend_schema_view(
    list=extend_schema(operation_id='categories_list'),
    create=extend_schema(operation_id='categories_create')
)
class CategoryListView(generics.ListCreateAPIView):
  #Below calculated the count of post in the database before it even hits the serializer
  queryset = Category.objects.all()
  serializer_class = CategorySerializer
  permission_classes = [permissions.AllowAny()]

  #Allow anyone to see Categories, but only logged-in users to create one
  def get_permissions(self):
    if self.request.method == 'POST':
      return [permissions.IsAuthenticated()]
    
    return [permissions.AllowAny()]
  
class CategoryPostListView(generics.ListAPIView):
  serializer_class = PostSerializer
  

  def get_queryset(self):
    #Grab the category name from the URL
    category_name = self.kwargs['category_name']
    #Filter posts by that category AND ensure they are published
    return Post.objects.filter(
      category__name__iexact=category_name,
      status='PB'
    ).order_by('-published_at')
  
class MyDraftListView(generics.ListAPIView):
  serializer_class = PostSerializer
  permission_classes = [permissions.IsAuthenticated]

  def get_queryset(self):
    #Only show the logged-in user's own drafts
    return Post.objects.filter(
      author=self.request.user,
      status = 'DF'
    ).order_by('-created_at')
  
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated()])
def publish_post(request, pk):
  
  try:
    post = Post.objects.get(pk=pk, author=request.user)

    post.status = 'PB'
    post.published_at = timezone.now()
    post.save()

    return Response({'status': 'Post published successfully!'}, status=200)
  except Post.DoesNotExist:
    return Response({'error': 'Post not found or unauthorized.'}, status=404)
