from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone


# Create your models here.
class Category(models.Model):
  name = models.CharField(max_length=100, unique=True)

  def __str__(self):
    return self.name
  

class Tag(models.Model):
  name = models.CharField(max_length=50, unique=True)

  def __str__(self):
    return self.name

class Post(models.Model):
  id = models.AutoField(primary_key=True)

  class Status(models.TextChoices):
    DRAFT = 'DF', 'Draft'
    PUBLISHED = 'PB', 'Published'

  status = models.CharField(max_length=2, choices=Status.choices, default=Status.DRAFT)
  published_at = models.DateTimeField(null=True, blank=True)

  #Required Fields
  title = models.CharField(max_length=255)
  content = models.TextField()

  #Relationships
  author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
  category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
  tags = models.ManyToManyField(Tag, blank=True)
  likes = models.ManyToManyField(User, related_name='liked_posts', blank=True)

  #Date Fields
  created_at = models.DateTimeField(auto_now_add=True)

  def save(self, *args, **kwargs):
    #Automatically set published_at when status changes to Published
    if self.status == self.Status.PUBLISHED and not self.published_at:
      self.published_at = timezone.now()

    super().save(*args, **kwargs)

  def __str__(self):
    return self.title
  
  def total_likes(self):
    return self.likes.count()


class Comment(models.Model):
  post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
  author = models.ForeignKey(User, on_delete=models.CASCADE)
  content = models.TextField()
  created_at = models.DateTimeField(auto_now_add=True)

  class Meta:
    ordering = ['-created_at'] #Newest comments first

  def __str__(self):
    return f"Comment by {self.author.username} on {self.post.title}"
  

class Like(models.Model):
  user = models.ForeignKey(User, on_delete=models.CASCADE)
  post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='post_likes')

  class Meta:
    constraints = [
      models.UniqueConstraint(fields=['user', 'post'], name='unique_like')
    ]
  
class Rating(models.Model):
  user = models.ForeignKey(User, on_delete=models.CASCADE)
  post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='ratings')
  score = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])

  class Meta:
    constraints = [models.UniqueConstraint(fields=['user', 'post'], name='unique_rating')]


class CategorySubscription(models.Model):
  user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='category_subscriptions')
  category = models.ForeignKey('Category', on_delete=models.CASCADE, related_name='subscribers')
  created_at = models.DateTimeField(auto_now_add=True)

  class Meta:
    #Prevents a user from subscribing to the same category twice
    constraints = [
      models.UniqueConstraint(fields=['user', 'category'], name='unique_category_sub')
    ]