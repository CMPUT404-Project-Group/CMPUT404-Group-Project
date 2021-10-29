from ..models import Inbox, User, Comment
from .utils import TestUtils
from django.test import TestCase
from django.shortcuts import get_object_or_404
from django.urls import reverse
from rest_framework.test import APIClient
from uuid import uuid4


class CommentTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = TestUtils.get_test_user()
        self.post = TestUtils.get_test_post(author=self.user)
    
    def test_create_comment(self):
        created_comment = Comment.objects.create_comment(                      
            author=self.user, 
            comment="TEST", 
            post=self.post
        )

        queried_comment = get_object_or_404(Comment, pk=created_comment.id)

        self.assertTrue(type(queried_comment), Comment)
    
    def test_comment_api_get(self):

        Comment.objects.create_comment(                      
            author=self.user, 
            comment=f"TEST", 
            post=self.post
        )

        context = {
            'author_id': self.user.id,
            'post_id': self.post.id
        }

        result = self.client.get(reverse('api:comments', kwargs=context))

        self.assertEqual(result.status_code, 200)
    
    def test_comment_api_get_paginated(self):
        
        for i in range(25):
            Comment.objects.create_comment(                      
                author=self.user, 
                comment=f"TEST-{i}", 
                post=self.post
            )

        context = {
            'author_id': self.user.id,
            'post_id': self.post.id
        }

        result_page_one = self.client.get(reverse('api:comments', kwargs=context) + "?page=1&size=5")
        result_last_page = self.client.get(reverse('api:comments', kwargs=context) + "?page=5&size=5")

        self.assertEqual(result_page_one.status_code, 200)
        self.assertEqual(result_last_page.status_code, 200)


    def X_test_comment_api_post(self):
        comment_json = {
            'type': 'comment',
            'comment': 'TEST_TEXT',
            'content_type': "text/plain",
            'id': str(uuid4()),
            'published': "2015-03-09T13:07:04+00:00"
        }

        context = {
            'author_id': self.user.id,
            'post_id': self.post.id
        }

        result = self.client.post(
            reverse('api:comments', kwargs=context),
            comment_json,
            format='json'
            )

        self.assertEqual(result.status_code, 204)