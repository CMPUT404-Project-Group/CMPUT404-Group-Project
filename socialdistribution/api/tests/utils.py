from ..models import Post, User


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
