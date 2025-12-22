import django_filters
from .models import Post

class PostFilter(django_filters.FilterSet):
  #Filtering for Category(using the 'name' slug)
  category = django_filters.CharFilter(
    field_name='category__name', #Filters by the name of the related Category model
    lookup_expr='iexact'
  )

  #Filter filtering for Author(using the 'username' slug)
  author = django_filters.CharFilter(
    field_name='author__username', #Filters by the username of the related User model
    lookup_expr='iexact'
  )

  #Filter by tag name(Many to many)
  tags = django_filters.CharFilter(field_name='tags__name', lookup_expr='iexact')

  #Date Filtering Refinement
  #This allows users to find posts on a specific day
  published_date = django_filters.DateFilter(field_name='published_date')

  #Allow filtering between two dates
  published_after = django_filters.DateFilter(field_name='published_date', lookup_expr='gte')#Greater than or Equal to
  published_before = django_filters.DateFilter(field_name='published_date', lookup_expr='lte') #Less Than or Equal to

  class Meta:
    model = Post
    #Include fields that can be filtered directly (e.g., published_date)
    fields = ['category', 'author', 'tags', 'published_date']
