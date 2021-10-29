
from django.test import TestCase

from ..models import Post, PostBuilder, User
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

    def test_share_post(self):
        author = TestUtils.get_test_user()
        visibility = Post.Visibility.PUBLIC
        unlisted = False

        test_shared_post = Post.objects.create_post(
            author, 
             'shared categories', 
             None,
             "Test shared post",
            "Shared post", 
            visibility, 
            unlisted)

        new_author = User.objects.create_user(
            email="newguy@gmail.com",
            displayName="New author",
            github="newguy",
            password="password",
            type=type
        )
    

        new_post = Post.objects.share_post(
            new_author, 
            "test", 
            "{} shared a post".format(new_author), 
            'New categories', 
            visibility, 
            unlisted, 
            test_shared_post)

        self.assertEqual(new_post.shared_post, test_shared_post)
        self.assertEqual(new_post.author, new_author)
        self.assertEqual(new_post.shared_post.author, author)