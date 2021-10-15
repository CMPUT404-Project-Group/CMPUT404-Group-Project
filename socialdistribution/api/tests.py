from django.core.exceptions import ValidationError
from django.test import TestCase
from rest_framework.test import APIClient
from django.urls import reverse
from .models import User, Post, PostBuilder
from urllib.parse import quote, uses_fragment

class TestUtils():
    def get_test_user(email='test@email.com', username='testuser', github='testgit', password='testpassword1', type='author'):
        return User.objects.create_user(
            email=email, 
            username=username, 
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

class GetAuthorTest(TestCase):
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(email="test@email.com", username="testuser", github="testgit", password="testpassword1", type="author")

    def test_get_author(self):
        # Arrange
        author = User.objects.get(username="testuser")
        author_id = quote(author.id, safe="") # need to quote id url to correct format
        expected = {'type': author.type, 'id': author.id, 'host': author.host, 'displayName': author.username, 'url': author.url, 'github': author.github}

        # Act
        response = self.client.get(reverse('api:author', kwargs={'author_id': author_id}))
        
        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content.decode('utf-8'), expected)


    def test_get_author_404(self):
        # Act
        response = self.client.get(reverse('api:author', args=('should404',)))

        # Assert
        self.assertEqual(response.status_code, 404)

class PostBuilderTest(TestCase):
    
    def setUp(self):
        self.post_builder = PostBuilder()

    def test_initializes_with_uuid(self):
        self.assertIsNotNone(self.post_builder.uuid)
    
    def test_initializes_with_proper_type(self):
        self.assertEqual(self.post_builder.type, 'post')
    
    def test_set_post_content_validation_error_no_content(self):
        self.assertRaises(ValidationError, self.post_builder.set_post_content, "title", "categories, are, neat")
    
    def test_set_post_metadata_first_assertion_error(self):
        author = TestUtils.get_test_user()
        visibility = Post.Visibility.PUBLIC
        unlisted = False
        self.assertRaises(AssertionError, self.post_builder.set_post_metadata, author, visibility, unlisted)
    
    def test_build_post(self):
        author = TestUtils.get_test_user()
        visibility = Post.Visibility.PUBLIC
        unlisted = False
        self.post_builder.set_post_content("Title", "Categories are neat", "Test Body")
        self.post_builder.set_post_metadata(author, visibility, unlisted)
        post = self.post_builder.get_post()

        self.assertIsInstance(post, Post)

class PostModelTest(TestCase):
    
    def test_text_post_in_DB(self):
        post = TestUtils.get_test_post(text_content="Body")

        post_by_title = Post.objects.get(title="Test Title")

        self.assertEqual(post, post_by_title)