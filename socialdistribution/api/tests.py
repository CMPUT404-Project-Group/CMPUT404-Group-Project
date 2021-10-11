from django.test import TestCase
from rest_framework.test import APIClient
from django.urls import reverse
from .models import User
from urllib.parse import quote
import json
import pprint


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

    def test_get_authors(self):
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
        self.assertEqual(User.objects.count(), 6)

        # Act
        response = self.client.get(reverse('api:authors'))
        content = json.loads(response.content.decode('utf-8'))

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertEqual(content["type"], "authors")
        self.assertIsInstance(content["items"], list)
        self.assertEqual(len(content["items"]), 5)
        for i in content["items"]:
            self.assertEqual(i["type"], "author")

    def test_get_authors_pagination(self):
        # Arrange - create a set of authors
        for i in range(0, 26):
            User.objects.create_user(email="test%s@email.com" % i, username='%s_testuser' % chr(
                97+i), github="testgit%s" % i, password="testpassword1", type="author")
        self.assertEqual(User.objects.count(), 26)

        # Act - get first page
        response = self.client.get(reverse('api:authors') + '?page=1')
        content = json.loads(response.content.decode('utf-8'))

        # Assert - first page
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content["items"]), 10)
        for i in range(0, 10):
            # assert the page is correct by checking ordering
            self.assertEquals(content["items"][i]["displayName"][0], chr(97+i))

        # Act - get second page
        response = self.client.get(reverse('api:authors') + '?page=2')
        content = json.loads(response.content.decode('utf-8'))

        # Assert - second page
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content["items"]), 10)
        for i in range(10, 20):
            # assert the page is correct by checking ordering
            self.assertEquals(content["items"][i-10]
                              ["displayName"][0], chr(97+i))

        # Act - get third page
        response = self.client.get(reverse('api:authors') + '?page=3')
        content = json.loads(response.content.decode('utf-8'))

        # Assert - third page
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content["items"]), 6)
        for i in range(20, 26):
            # assert the page is correct by checking ordering
            self.assertEquals(content["items"][i-20]
                              ["displayName"][0], chr(97+i))

        # Act - set page size
        response = self.client.get(reverse('api:authors') + '?page=1&size=5')
        content = json.loads(response.content.decode('utf-8'))

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content["items"]), 5)
        for i in range(0, 5):
            # assert the page is correct by checking ordering
            self.assertEquals(content["items"][i]["displayName"][0], chr(97+i))

        # Act - set page size
        response = self.client.get(reverse('api:authors') + '?page=4&size=5')
        content = json.loads(response.content.decode('utf-8'))

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content["items"]), 5)
        for i in range(20, 25):
            # assert the page is correct by checking ordering
            self.assertEquals(content["items"][i-20]
                              ["displayName"][0], chr(97+i-5))
