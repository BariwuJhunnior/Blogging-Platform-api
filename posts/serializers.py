from rest_framework import serializers
from .models import Post, Category, Tag, Comment, Rating
from .utils import get_social_share_links
from drf_spectacular.utils import extend_schema_field
from drf_spectacular.types import OpenApiTypes
import markdown
import bleach

class PostSerializer(serializers.ModelSerializer):
  # Use StringRelatedField to show the author's username instead of their ID
  author = serializers.ReadOnlyField(source='author.username')
  # Use SlugRelatedField to show category name, and make it required
  category_name = serializers.SlugRelatedField(
    source='category', # Link to the 'category' field in the Post model
    slug_field='name',
    queryset = Category.objects.all(), # Used for validation in POST/PUT
  )

  #This field will show the rendered HTML
  content_html = serializers.SerializerMethodField()

  # Tags are optional, allow reading/writing names
  tags = serializers.SlugRelatedField(
    many=True,
    slug_field='name', 
    queryset=Tag.objects.all(),
    required=False, #Tages are optional requirement
  )

  likes_count = serializers.IntegerField(read_only=True)
  avg_rating = serializers.FloatField(read_only=True)

  share_links = serializers.SerializerMethodField()

  class Meta:
    model = Post
    fields = ['id', 'title', 'content', 'author', 'category_name', 'published_at', 'created_at', 'tags', 'likes_count', 'avg_rating', 'share_links', 'content_html']

    read_only_fields = ('author', 'created_at') #These are set by the server, not the user

  def get_content_html(self, obj):
    

    #Converts the raw 'content' (Markdown) into HTML
    #extensions=['extra'] adds support for tables, footnotes, etc.
    html =  markdown.markdown(obj.content, extensions=['extra', 'codehilite'])

    #Define which HTML tags are allowed
    allowed_tags = [
      'p', 'b', 'i', 'u', 'em', 'string', 'a', 'h1', 'h2', 'h3', 'li', 'ul', 'ol', 'code', 'pre'
    ]
    allowed_attrs = {'a': ['href', 'title']}

    return bleach.clean(html, tags=allowed_tags, attributes=allowed_attrs)

  @extend_schema_field(OpenApiTypes.OBJECT)
  def get_share_links(self, obj):
    #We only show links for published posts
    if obj.status == Post.Status.PUBLISHED:
      url = f"https://myblog.com/posts/{obj.id}"
      return get_social_share_links(url, obj.title)
    return None


class CommentSerializer(serializers.ModelSerializer):
  author = serializers.ReadOnlyField(source='author.username')

  class Meta:
    model = Comment
    fields = ['id', 'post', 'author', 'content', 'created_at']


class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = ['score']

