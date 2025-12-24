import urllib.parse

def get_social_share_links(post_url, post_title):
  encoded_url = urllib.parse.quote(post_url)
  encoded_title = urllib.parse.quote(post_title)

  return {
    "X": f'https://x.com/intent/tweet?url={encoded_url}&text={encoded_title}',
    "facebook": f"https://www.facebook.com/sharer/sharer.php?u={encoded_url}",
    "linkedin": f"https://www.linkedin.com/shareArticle?mini=true&url={encoded_url}&title={encoded_title}"
  }