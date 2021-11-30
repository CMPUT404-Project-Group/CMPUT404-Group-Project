from json import loads
from django.test import TestCase
from rest_framework.test import APIClient
from django.urls import reverse

from ..models import Inbox, User

from .utils import TestUtils


class InboxTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = TestUtils.get_test_user()
        self.num_inbox = 6
        TestUtils.setup_inbox(author_id=self.user.id,
                              num_messages=self.num_inbox)

    def test_get_inbox(self):
        # Arrange
        author_id = self.user.id

        # Act
        self.client.force_authenticate(user=User.objects.get(displayName=self.user.displayName))
        response = self.client.get(
            reverse('api:inbox', kwargs={'author_id': author_id}))

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertGreater(
            len(loads(response.content)['items']), 0)

    def test_get_inbox_paginated(self):
        # Arrange
        author_id = self.user.id

        # Act
        self.client.force_authenticate(user=User.objects.get(displayName=self.user.displayName))
        response = self.client.get(
            reverse('api:inbox', kwargs={'author_id': author_id}) + '?page=1&size=5')

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertEquals(
            len(loads(response.content)['items']), 5)

        response = self.client.get(
            reverse('api:inbox', kwargs={'author_id': author_id}) + '?page=2&size=5')

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertEquals(
            len(loads(response.content)['items']), 1)

    def get_inbox_no_auth(self):
        # Arrange
        author_id = self.user.id

        content_object = TestUtils.get_test_post(
            author=User.objects.get(id=author_id), text_content="This is a test post post!")

        # Act
        response = self.client.post(
            reverse('api:inbox', kwargs={'author_id': 1}), {'type': 'post', 'object_id': content_object.id}, format='json')

        # Assert
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Inbox.objects.count(), self.num_inbox)

    def test_post_inbox(self):
        # Arrange
        author_id = self.user.id

        content_object = TestUtils.get_test_post(
            author=User.objects.get(id=author_id), text_content="This is a test post post!")

        # Act
        self.client.force_authenticate(user=User.objects.get(displayName=self.user.displayName))
        response = self.client.post(
            reverse('api:inbox', kwargs={'author_id': author_id}), {'type': 'post', 'object_id': content_object.id}, format='json')

        # Assert
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Inbox.objects.count(), self.num_inbox+1)

    def test_post_inbox_fail(self):
        # Arrange
        author_id = self.user.id

        content_object = TestUtils.get_test_post(
            author=User.objects.get(id=author_id), text_content="This is a test post post!")

        # Act
        self.client.force_authenticate(user=User.objects.get(displayName=self.user.displayName))
        response = self.client.post(
            reverse('api:inbox', kwargs={'author_id': 1}), {'type': 'post', 'object_id': content_object.id}, format='json')

        # Assert
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Inbox.objects.count(), self.num_inbox)

    def test_post_delete_inbox(self):
        # Arrange
        author_id = self.user.id

        # Act
        self.client.force_authenticate(user=User.objects.get(displayName=self.user.displayName))
        response = self.client.delete(
            reverse('api:inbox', kwargs={'author_id': author_id}))

        # Assert
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Inbox.objects.count(), 0)

    def test_post_delete_inbox_no_auth(self):
        # Arrange
        author_id = self.user.id

        # Act
        response = self.client.delete(
            reverse('api:inbox', kwargs={'author_id': author_id}))

        # Assert
        self.assertEqual(response.status_code, 401)

    def test_post_bad_request(self):
        # Arrange
        author_id = self.user.id

        # Act
        self.client.force_authenticate(user=User.objects.get(displayName=self.user.displayName))
        response = self.client.put(
            reverse('api:inbox', kwargs={'author_id': author_id}))

        # Assert
        self.assertEqual(response.status_code, 405)
