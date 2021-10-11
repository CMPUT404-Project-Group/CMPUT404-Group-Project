from django.test import TestCase
from rest_framework.test import APIClient
from django.urls import reverse
from .models import User
from urllib.parse import quote
import json


class AuthorTest(TestCase):
    """
    Tests for the /author/<str:author_id>/ endpoint (GET and POST).
    """

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="test@email.com", username="testuser", github="testgit", password="testpassword1", type="author")

    def test_get_author(self):
        # Arrange
        author = User.objects.get(username="testuser")
        # need to quote id url to correct format
        author_id = quote(author.id, safe="")

        expected = {'type': author.type, 'id': author.id, 'host': author.host,
                    'displayName': author.username, 'url': author.url, 'github': author.github}

        # Act
        response = self.client.get(
            reverse('api:author', kwargs={'author_id': author_id}))

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content.decode('utf-8'), expected)

    def test_get_author_404(self):
        # Act
        response = self.client.get(reverse('api:author', args=('should404',)))

        # Assert
        self.assertEqual(response.status_code, 404)


class AuthorsTest(TestCase):
    """
    Tests for the /authours/ endpoint 
    """

    def SetUp(self):
        self.client = APIClient()

    def get_authors(self):
        # Arrange - create a set of authors
        for i in range(0, 5):
            User.objects.create_user(email="test%s@email.com" % i, username="testuser%s" %
                                     i, github="testgit%s" % i, password="testpassword1", type="author")

        # Act
        response = self.client.get(reverse('api:authors'))
        content = json.loads(response.content.decode('utf-8'))

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertEqual(content["type"], "authors")
        self.assertIsInstance(content["items"], list)
        self.assertEqual(len(content["items"]), 5)

    def test_get_authors_only(self):
        # Arrange - create a set of authors
        for i in range(0, 5):
            User.objects.create_user(email="test%s@email.com" % i, username="testuser%s" %
                                     i, github="testgit%s" % i, password="testpassword1", type="author")

        # Arrange - add a server adimn that should not be returned
        User.objects.create_user(email="admin@email.com", username="testadmin",
                                 password="testpassword1", type="server-admin")

        # Act
        response = self.client.get(reverse('api:authors'))
        content = json.loads(response.content.decode('utf-8'))

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertEqual(content["type"], "authors")
        self.assertIsInstance(content["items"], list)
        self.assertEqual(User.objects.count(), 6)
        self.assertEqual(len(content["items"]), 5)
        for i in content["items"]:
            self.assertEqual(i["type"], "author")

    def test_get_authors_pagination(self):

        # Act
        response = self.client.get(reverse('api:authors'))
        content = json.loads(response.content.decode('utf-8'))

        # Assert
