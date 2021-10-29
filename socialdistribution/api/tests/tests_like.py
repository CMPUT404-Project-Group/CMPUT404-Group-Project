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
        self.like = TestUtils.get_test_like(author=self.user, content_object=self.post)

    def test_GET_api_post_likes(self):
        self.assertTrue(False)
    
    def test_GET_api_comment_likes(self):
        self.assertTrue(False)
    
    def test_GET_api_author_liked(self):

        for i in range(5):
            post = TestUtils.get_test_post(author=self.user, title=f"TEST-TITLE-{i}")
            like = TestUtils.get_test_like(author=self.user, content_object=post)

        context = {
            'author': self.user,
        }

        response = self.client.get(reverse('api:liked'), kwargs=context)

        self.assertEqual(response.status_code, 200)

