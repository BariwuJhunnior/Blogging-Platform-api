from typing import Any, Dict
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from .models import Post, Category

class PostTests(APITestCase):
  def setUp(self):
    #Create a user and a category for testing
    self.user = User.objects.create_user(username='author', password='password123')
    self.category = Category.objects.create(name='Tech')
    self.post = Post.objects.create(title='T1', content='C1', author=self.user, category=self.category)

    #Create a post owned by our User
    self.post = Post.objects.create(
      title='Initial Post',
      content='Hello World',
      author=self.user,
      category=self.category
    )
    self.url = reverse('post-list-create') #Matches path name in urls.py

  #Test 2: Read
  def test_view_posts_list(self):
    response = self.client.get(self.url)  # type: ignore
    self.assertEqual(response.status_code, status.HTTP_200_OK)
    # Check if the post we created in setUp is in the response
    self.assertEqual(len(response.data), 1)  # type: ignore

  def test_only_author_can_delete(self):
    hacker = User.objects.create_user(username='hacker', password='password123')
    self.client.force_authenticate(user=hacker)
    response = self.client.delete(f'/posts/{self.post.id}/')
    self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

  #Test 3: Permissions
  def test_unauthorized_delete_fails(self):
    #second User
    other_user = User.objects.create_user(username='hacker', password='password123')
    #Login as the second user
    self.client.force_authenticate(user=other_user)  # type: ignore

    #Attempt to delete the post owned by the first user
    detail_url = reverse('post-detail', kwargs={'pk': self.post.id})  # type: ignore
    response = self.client.delete(detail_url)

    #4. Assert that request was FORBIDDEN
    self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

  def test_create_post_authenticated(self):
    #1. Log in the user
    self.client.force_authenticate(user=self.user)  # type: ignore

    #2. Define the data for the new post 
    data = {  # type: Dict[str, Any]
      'title': 'New Test Post',
      'content': 'This is a post created via automated tests.',
      'category_name': 'Tech', #Using the slug field we set up in our serializer
      'tags': []
    }

    #3. Send the POST request
    response = self.client.post(self.url, data)

    #4. Assertions (The 'Check' phase)
    #Check if it was created (201 Created)
    self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    #Verify the database actually has 2 posts now
    self.assertEqual(Post.objects.count(), 2)

    #Crucial: Check if the author was automatically assigned to 'testuser'
    new_post = Post.objects.get(title='New Test Post')
    self.assertEqual(new_post.author, self.user)

  #Testing Search and Filtering
  def test_filter_by_category(self):
    #1. Create additional category and post for contrast
    other_cat = Category.objects.create(name='Cooking')
    Post.objects.create(
      title="How to Bake Bread",
      content="Use flour and water",
      author=self.user,
      category=other_cat
    )

    #2. Hit the endpoint with a category filter (?category=Tech)
    url = f"{self.url}?category=Tech"
    response = self.client.get(url)

    #3. Assertions
    self.assertEqual(response.status_code, status.HTTP_200_OK)
    #Expect only 1 post (the Tech one), not both!
    self.assertEqual(len(response.data), 1)  # type: ignore
    self.assertEqual(response.data[0]['title'], "Initial Post")  # type: ignore

  def test_search_posts(self):
    # Create a post with a very specific keyword
    Post.objects.create(
      title="Django Tips",
      content="Learn about Serializers here.",
      author=self.user,
      category=self.category
    )

    #Search for that Keyword
    url= f"{self.url}?search=Serializers"
    response = self.client.get(url)

    self.assertEqual(len(response.data), 1)  # type: ignore
    self.assertIn("Serializers", response.data[0]['content'])  # type: ignore 


  #Negative Test (Unauthorized Create)
  def test_create_post_unauthenticated_fails(self):
    #Ensure no one is logged in 
    self.client.logout()

    data = {  # type: Dict[str, Any]
      'title': 'Ghost Post',
      'content': 'Should fail',
    }
    response = self.client.post(self.url, data)

    #Assert that it blocks the user (401 Unauthorized)
    self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
