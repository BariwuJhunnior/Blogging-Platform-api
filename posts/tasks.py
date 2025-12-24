from celery import shared_task
from django.core.mail import send_mail

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