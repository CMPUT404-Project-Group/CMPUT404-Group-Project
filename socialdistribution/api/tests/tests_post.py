
from django.test import TestCase

from ..models import Post, PostBuilder
from .utils import TestUtils


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
