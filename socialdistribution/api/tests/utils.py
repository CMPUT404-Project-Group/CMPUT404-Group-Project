from ..models import Inbox, Post, User


class TestUtils():
    def get_test_user(email='test@email.com', displayName='testuser', github='testgit', password='testpassword1', type='author'):
        return User.objects.create_user(
            email=email,
            displayName=displayName,
            github=github,
            password=password,
            type=type
        )

    def get_test_post(author=None, categories="test, categories, are, fun", image_content=None, text_content=None, title="Test Title", visibility=Post.Visibility.PUBLIC, unlisted=False):

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

    def setup_inbox(author_id, num_messages):
        for i in range(num_messages):
            content_object = TestUtils.get_test_post(
                author=User.objects.get(id=author_id), text_content="Inbox Post %s" % i)
            Inbox.objects.create(author_id=author_id,
                                 content_object=content_object)
