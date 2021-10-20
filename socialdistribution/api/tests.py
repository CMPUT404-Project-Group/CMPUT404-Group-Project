import json
import os
from uuid import uuid4

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse
from dotenv import load_dotenv
from rest_framework.test import APIClient

from .models import Post, PostBuilder, User

load_dotenv()
HOST_API_URL = os.getenv("HOST_API_URL")
GITHUB_URL = os.getenv("GITHUB_URL")


class TestUtils():
    def get_test_user(email='test@email.com', displayName='testuser', github='testgit', password='testpassword1', type='author'):
        return User.objects.create_user(
            email=email,
            displayName=displayName,
            github=github,
            password=password,
            type=type
        )

    def get_test_post(
            author=None, categories="test, categories, are, fun", image_content=None, text_content=None,
            title="Test Title", visibility=Post.Visibility.PUBLIC, unlisted=False):

        if not author:
            author = TestUtils.get_test_user()

        return Post.objects.create_post(
            author=author,
            categories=categories,
            image_content=image_content,
            text_content=text_content,
            title=title,
            visibility=visibility,
            unlisted=unlisted
        )


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

    def SetUp(self):
        self.client = APIClient()

    def test_get_authors(self):
        # Arrange - create a set of authors
        for i in range(0, 5):
            User.objects.create_user(email="test%s@email.com" % i, displayName="testuser%s" %
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
            User.objects.create_user(email="test%s@email.com" % i, displayName="testuser%s" %
                                     i, github="testgit%s" % i, password="testpassword1", type="author")

        # Arrange - add a server adimn that should not be returned
        User.objects.create_user(email="admin@email.com", displayName="testadmin",
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
            User.objects.create_user(email="test%s@email.com" % i, displayName='%s_testuser' % chr(
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

    def test_unauthorized_method(self):
        # Act
        response = self.client.delete(reverse('api:authors'))

        # Assert
        self.assertEqual(response.status_code, 405)


class PostBuilderTest(TestCase):

    def setUp(self):
        self.post_builder = PostBuilder()

    def test_initializes_with_id(self):
        self.assertIsNotNone(self.post_builder.id)

    def test_initializes_with_proper_type(self):
        self.assertEqual(self.post_builder.type, 'post')

    def test_set_post_metadata_first_assertion_error(self):
        author = TestUtils.get_test_user()
        visibility = Post.Visibility.PUBLIC
        unlisted = False
        self.assertRaises(
            AssertionError, self.post_builder.set_post_metadata, author, visibility, unlisted)

    def test_build_post(self):
        author = TestUtils.get_test_user()
        visibility = Post.Visibility.PUBLIC
        unlisted = False
        self.post_builder.set_post_content(
            "Title", "Categories are neat", "Test Body")
        self.post_builder.set_post_metadata(author, visibility, unlisted)
        post = self.post_builder.get_post()

        self.assertIsInstance(post, Post)
