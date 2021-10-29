from ..models import User, Comment, Like
from .utils import TestUtils
from django.test import TestCase
from rest_framework.test import APIClient

class LikeTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = TestUtils.get_test_user()
        self.post = TestUtils.get_test_post(author=self.user)

    def test_POST_api_author(self):
        self.assertTrue(False)

    def test_GET_api_post_likes(self):
        self.assertTrue(False)
    
    def test_GET_api_comment_likes(self):
        self.assertTrue(False)
    
    def test_GET_api_author_liked(self):
        self.assertTrue(False)