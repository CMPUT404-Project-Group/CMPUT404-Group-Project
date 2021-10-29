from django.http.request import HttpRequest
from ..models import User, Comment, Like
from .utils import TestUtils
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from uuid import uuid4

class LikeTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = TestUtils.get_test_user()
        self.post = TestUtils.get_test_post(author=self.user)
        self.comment = TestUtils.get_test_comment(author=self.user, post=self.post)

    def test_GET_api_post_likes(self):
        like = TestUtils.get_test_like(author=self.user, content_object=self.post)

        context = {
            'author_id': self.user.id,
            'post_id': self.post.id
        }

        response = self.client.get(reverse('api:like-post', kwargs=context))

        self.assertEqual(response.status_code, 200)
    
    def test_GET_api_comment_likes(self):
        like = TestUtils.get_test_like(author=self.user, content_object=self.comment)

        context = {
            'author_id': self.user.id,
            'post_id': self.post.id,
            'comment_id': self.comment.id
        }

        response = self.client.get(reverse('api:like-comment', kwargs=context))

        self.assertEqual(response.status_code, 200)
    
    def test_GET_api_author_liked(self):

        for i in range(5):
            post = TestUtils.get_test_post(author=self.user, title=f"TEST-TITLE-{i}")
            like = TestUtils.get_test_like(author=self.user, content_object=post)

        #Couldn't get reverse to work 
        response = self.client.get(f"http://localhost:8000/api/author/{self.user.id}/liked?format=json")

        self.assertEqual(response.status_code, 200)

