from rest_framework import serializers
from .models import Post, Category, Tag, Comment, Rating
from .utils import get_social_share_links
from drf_spectacular.utils import extend_schema_field
from drf_spectacular.types import OpenApiTypes
import markdown
import bleach


class CommentSerializer(serializers.ModelSerializer):
  author_username = serializers.ReadOnlyField(source='author.username')

  class Meta:
    model = Comment
    fields = ['id', 'post', 'author_username', 'content', 'created_at']
    read_only_fields = ['author', 'post']

class PostSerializer(serializers.ModelSerializer):
  # Use StringRelatedField to show the author's username instead of their ID
  author = serializers.ReadOnlyField(source='author.username')
  # Use SlugRelatedField to show category name, and make it required
  category = serializers.SlugRelatedField(
    queryset=Category.objects.all(),
    slug_field='name'
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

  likes_count = serializers.ReadOnlyField(source='total_likes')
  has_liked = serializers.SerializerMethodField()
  avg_rating = serializers.FloatField(read_only=True)

  #share_links = serializers.SerializerMethodField()

  status_display = serializers.CharField(source='get_status_display', read_only=True)
  comments = CommentSerializer(many=True, read_only=True)

  class Meta:
    model = Post
    fields = ['id', 'title', 'content', 'author', 'status_display', 'category', 'created_at', 'has_liked', 'likes_count', 'comments', 'content_html', 'avg_rating', 'tags', 'status']

    read_only_fields = ('author',) #These are set by the server, not the user
    extra_kwargs = {
      'status': {'required': True}
    }

  @extend_schema_field(serializers.BooleanField)
  def get_has_liked(self, obj):
    request = self.context.get('request')
    if request is None or not request.user.is_authenticated:
      return False
    
    #Check if the user exists in the ManyToMany relationship
    return obj.likes.filter(pk=request.user.pk).exists()

  @extend_schema_field(OpenApiTypes.STR)
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


class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = ['score']


class CategorySerializer(serializers.ModelSerializer):
  post_count = serializers.SerializerMethodField()

  class Meta:
    model = Category
    fields = ['id', 'name', 'post_count']

  def get_post_count(self, obj):
    #Counts only posts that are Published
    return Post.objects.filter(category=obj, status='PB').count()