from django.urls import path
from .views import (
  PostListCreateView, PostDetailView, CommentListCreateView, CommentDetailView, LikePostView, RatePostView, TopPostsView, PostShareView, SubscribeCategoryView, UserFeedView, GlobalFeedView, CategoryListView, MyDraftListView, publish_post, CategoryPostListView, PostPublishView
)
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
  #GET (List) and POST (Create)
  path('', PostListCreateView.as_view(), name='post-list'),
  #GET (Retrieve), PUT/PATCH (Update), DELETE(Destroy)
  path('<int:pk>/', PostDetailView.as_view(), name='post-detail'),

  #Comments
  path('<int:post_pk>/comments/', CommentListCreateView.as_view(), name='post-comments' ),
  path('comments/<int:pk>/', CommentDetailView.as_view(), name='comment-detail'),

  #Engagements (Likes/Ratings)
  path('<int:pk>/like/', LikePostView.as_view(), name='post-like'),
  path('<int:pk>/rate/', RatePostView.as_view(), name='post-rate'),
  path('top/', TopPostsView.as_view(), name='top-posts'),
  path('<int:pk>/share/', PostShareView.as_view(), name='post-share'),
  path('<int:pk>/publish/', PostPublishView.as_view(), name='post-publish'),
  
  
  #Category
  path('categories/', CategoryListView.as_view(), name='category-list'),
  path('categories/<int:category_id>/subscribe/', SubscribeCategoryView.as_view(), name='category-subscribe'),
  path('categories/<str:category_name>/', CategoryPostListView.as_view(), name='category-posts'),

  #Feed
  path('feed/', UserFeedView.as_view(), name='user-feed'),
  path('explore/', GlobalFeedView.as_view(), name='explore'),

  #Drafts
  path('drafts/', MyDraftListView.as_view(), name='my-drafts'),


  #Documentation
  path('schema/', SpectacularAPIView.as_view(), name='schema'),
  path('docs/swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
  path('docs/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
  path('<int:post_pk>/comments/', CommentListCreateView.as_view(), name='comment-list-create'),
  path('comments/<int:pk>/', CommentDetailView.as_view(), name='comment-detail'),
]
