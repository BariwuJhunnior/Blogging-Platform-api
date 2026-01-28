from celery import shared_task
from django.core.mail import send_mail
from .models import Post, CategorySubscription
from users.models import Follow


@shared_task
def send_rating_notification_email(author_email, author_username, post_title):
  send_mail(
    subject='Your post got a 5-star rating',
    message=f"Hi {author_username}, \n\nGreat news! Your post '{post_title}' just received a 5-star rating.",
    from_email='notifications@blogapi.com',
    recipient_list=[author_email],
    fail_silently=False
  )


@shared_task
def share_post_via_email(post_title, post_url, recipient_email, sender_name):
  subject = f"{sender_name} shared a post with you: {post_title}"
  message = f"Hi!\n\n{sender_name} thought you'd like this post: '{post_title}'.\n\nYou can read it here: {post_url}"

  send_mail(
    subject=subject,
    message=message,
    from_email='notifications@blogapi.com',
    recipient_list=[recipient_email],
    fail_silently=False,
  )

@shared_task
def notify_subscribers(post_id):
  post = Post.objects.get(pk=post_id)

  #1. Get emails of people following the author
  author_followers = Follow.objects.filter(followed_user=post.author).values_list('follower__email', flat=True)

  #2. Get emails of people subscribed to the category
  category_subs = CategorySubscription.objects.filter(category=post.category).values_list('user__email', flat=True)

  #3. Combine and remove duplicates
  recipient_list = list(set(list(author_followers) + list(category_subs)))

  #4. Remove empty emails
  recipient_list = [email for email in recipient_list if email]

  if recipient_list:
    category_name = post.category.name if post.category else "General"
    send_mail(
      subject=f"New Post: {post.title}",
      message=f"{post.author.username} just published a new post in {category_name}!\n\nRead it here: http://myblog.com/posts/{post.id}/",
      from_email='notifications@blogapi.com',
      recipient_list=recipient_list,
      fail_silently=False,
    )
