import json
import os
from uuid import uuid4

from django.test import TestCase
from django.urls import reverse
from dotenv import load_dotenv
from rest_framework.test import APIClient

from ..models import User

from django.conf import settings
HOST_API_URL = settings.HOST_API_URL
GITHUB_URL = settings.GITHUB_URL


class AuthorTest(TestCase):
    """
    Tests for the /author/<str:author_id>/ endpoint (GET and POST).
    """

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="test@email.com", displayName="testuser", github="testgit", password="testpassword1", type="author")

    def test_get_author(self):
        # Arrange
        author = User.objects.get(displayName="testuser")
        author_id = author.id
        expected = {'type': author.type, 'id': HOST_API_URL+'author/'+str(author.id), 'host': author.host,
                    'displayName': author.displayName, 'url': author.url, 'github': GITHUB_URL+author.github}

        # Act
        response = self.client.get(
            reverse('api:author', kwargs={'author_id': author_id}))

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content.decode('utf-8'), expected)

    def test_get_author_404(self):
        # Act
        response = self.client.get(reverse('api:author', args=(uuid4(),)))

        # Assert
        self.assertEqual(response.status_code, 404)

    def test_post_author(self):
        # Arrange
        author = User.objects.get(displayName="testuser")
        author_id = author.id

        # Act
        response = self.client.post(reverse('api:author', kwargs={'author_id': author_id}), {'id': author_id,
                                    'displayName': 'updated_name'}, format='json')

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.content), 0)
        author = User.objects.get(id=author_id)
        self.assertEqual(author.displayName, 'updated_name')

    def test_post_author_404(self):
        # Arrange
        author = User.objects.get(displayName="testuser")
        author_id = author.id

        # Act
        response = self.client.post(reverse('api:author', kwargs={'author_id': uuid4()}), {'id': author_id,
                                    'displayName': 'updated_name'}, format='json')

        # Assert
        self.assertEqual(response.status_code, 404)
        author = User.objects.get(id=author_id)
        self.assertEqual(author.displayName, 'testuser')

    def test_unauthorized_method(self):
        # Arrange
        author = User.objects.get(displayName="testuser")
        author_id = author.id

        # Act
        response = self.client.put(
            reverse('api:author', kwargs={'author_id': author_id}))

        # Assert
        self.assertEqual(response.status_code, 405)


class AuthorsTest(TestCase):
    """
    Tests for the /authours/ endpoint
    """

    def setUp(self):
        self.client = APIClient()

    def test_get_authors(self):
        # Arrange - create a set of authors
        for i in range(0, 5):
            User.objects.create_user(email="test%s@email.com" % i, displayName="testuser%s" %
                                     i, github="testgit%s" % i, password="testpassword1", type="author")

        # Act
        self.client.force_authenticate(user=User.objects.get(displayName="testuser0"))
        response = self.client.get(reverse('api:authors'))
        content = json.loads(response.content.decode('utf-8'))

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertEqual(content["type"], "authors")
        self.assertIsInstance(content["data"], list)
        self.assertEqual(len(content["data"]), 5)

    def test_get_authors_only(self):
        # Arrange - create a set of authors
        for i in range(0, 5):
            User.objects.create_user(email="test%s@email.com" % i, displayName="testuser%s" %
                                     i, github="testgit%s" % i, password="testpassword1", type="author")

        # Arrange - add a server adimn that should not be returned
        User.objects.create_user(email="admin@email.com", displayName="testadmin",
                                 password="testpassword1", type="server-admin")
        self.assertEqual(User.objects.count(), 6)

        # Act
        self.client.force_authenticate(user=User.objects.get(displayName="testuser0"))
        response = self.client.get(reverse('api:authors'))
        content = json.loads(response.content.decode('utf-8'))

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertEqual(content["type"], "authors")
        self.assertIsInstance(content["data"], list)
        self.assertEqual(len(content["data"]), 5)
        for i in content["data"]:
            self.assertEqual(i["type"], "author")

    def test_get_authors_pagination(self):
        # Arrange - create a set of authors
        for i in range(0, 26):
            User.objects.create_user(email="test%s@email.com" % i, displayName='%s_testuser' % chr(
                97+i), github="testgit%s" % i, password="testpassword1", type="author")
        self.assertEqual(User.objects.count(), 26)

        # Act - get first page
        self.client.force_authenticate(user=User.objects.get(displayName="a_testuser"))
        response = self.client.get(reverse('api:authors') + '?page=1')
        content = json.loads(response.content.decode('utf-8'))

        # Assert - first page
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content["data"]), 10)
        for i in range(0, 10):
            # assert the page is correct by checking ordering
            self.assertEquals(content["data"][i]["displayName"][0], chr(97+i))

        # Act - get second page
        response = self.client.get(reverse('api:authors') + '?page=2')
        content = json.loads(response.content.decode('utf-8'))

        # Assert - second page
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content["data"]), 10)
        for i in range(10, 20):
            # assert the page is correct by checking ordering
            self.assertEquals(content["data"][i-10]
                              ["displayName"][0], chr(97+i))

        # Act - get third page
        response = self.client.get(reverse('api:authors') + '?page=3')
        content = json.loads(response.content.decode('utf-8'))

        # Assert - third page
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content["data"]), 6)
        for i in range(20, 26):
            # assert the page is correct by checking ordering
            self.assertEquals(content["data"][i-20]
                              ["displayName"][0], chr(97+i))

        # Act - set page size
        response = self.client.get(reverse('api:authors') + '?page=1&size=5')
        content = json.loads(response.content.decode('utf-8'))

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content["data"]), 5)
        for i in range(0, 5):
            # assert the page is correct by checking ordering
            self.assertEquals(content["data"][i]["displayName"][0], chr(97+i))

        # Act - set page size
        response = self.client.get(reverse('api:authors') + '?page=4&size=5')
        content = json.loads(response.content.decode('utf-8'))

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content["data"]), 5)
        for i in range(20, 25):
            # assert the page is correct by checking ordering
            self.assertEquals(content["data"][i-20]
                              ["displayName"][0], chr(97+i-5))

    def test_unauthorized_method(self):
        # Act
        User.objects.create_user(email="test@email.com", displayName='testuser', github="testgit",
         password="testpassword1", type="author")
        self.client.force_authenticate(user=User.objects.get(displayName="testuser"))
        response = self.client.delete(reverse('api:authors'))

        # Assert
        self.assertEqual(response.status_code, 405)
