from django.test import Client, TestCase
from api.models import User
from api.tests.utils import TestUtils
class FrontEndRouteTest(TestCase):
    """
    Tests that all routes return correct repsonses and use correct templates. 

    """

    def setUp(self):
        self.c = Client()
        self.dn = 'frontend'
        self.p = 'frontendtests1'
        self.user = User.objects.create_user(
            email='frontend@test.com',
            displayName=self.dn,
            github='frontend',
            password=self.p,
            type='author'
        )

    def test_login_form(self):
        response = self.c.get('/app/accounts/login/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/login.html')

    def test_register_form(self):
        response = self.c.get('/app/register/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/register.html')

    def test_index(self):
        # should redirect if user not logged in
        response = self.c.get('/app/')
        self.assertEqual(response.status_code, 302)
        self.assertTemplateNotUsed(response, 'app/index.html')

        # log in
        self.c.login(displayName=self.dn, password=self.p)
        response = self.c.get('/app/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/index.html')

        self.c.logout()

    def test_inbox(self):
        # should redirect if user not logged in
        response = self.c.get(f'/app/author/{self.user.id}/inbox/')
        self.assertEqual(response.status_code, 302)
        self.assertTemplateNotUsed(response, 'app/inbox.html')

        # CAN'T TEST THIS UNLESS WE MOCK THE INBOX REQUEST SOMEHOW?
        # # log in
        # self.c.login(displayName=self.dn, password=self.p)
        # response = self.c.get(f'/app/author/{self.user.id}/inbox/')
        # self.assertEqual(response.status_code, 200)
        # self.assertTemplateUsed(response, 'app/inbox.html')
        # self.c.logout()

    def _create_post(self):
        self.c.login(displayName=self.dn, password=self.p)
        response = self.c.get(f'/app/create-post/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'posts/create_post.html')

    def test_edit_post(self):
        self.c.login(displayName=self.dn, password=self.p)
        post = TestUtils.get_test_post(author=self.user)
        response = self.c.get(f'/app/posts/edit-post/{post.id}')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'posts/edit_post.html')

        self.c.logout()
   
    def test_delete_post(self):
        # should redirect if user not logged in
        post = TestUtils.get_test_post(author=self.user)
        response = self.c.get(f'/app/posts/delete-post/{post.id}')
        self.assertEqual(response.status_code, 403)
        self.assertTemplateNotUsed(response, 'app/inbox.html')

        # should allow logged in user to delete
        self.c.login(displayName=self.dn, password=self.p)
        response = self.c.get(f'/app/posts/delete-post/{post.id}')
        self.assertEqual(response.status_code, 200)

        self.c.logout()

    def test_view_post(self):
        self.c.login(displayName=self.dn, password=self.p)
        post = TestUtils.get_test_post(author=self.user)
        response = self.c.get(f'/app/posts/{post.id}')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'posts/view_post.html')

        self.c.logout()

    def test_create_comment(self):
        self.c.login(displayName=self.dn, password=self.p)
        post = TestUtils.get_test_post(author=self.user)
        response = self.c.get(f'/app/posts/{post.id}/create-comment')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'comments/create_comment.html')

        self.c.logout()

    def test_view_comments(self):
        self.c.login(displayName=self.dn, password=self.p)
        post = TestUtils.get_test_post(author=self.user)
        response = self.c.get(f'/app/posts/{post.id}/comments')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'comments/comments.html')

        self.c.logout()

    def test_view_profile(self):
        # should redirect if not logged in 
        response = self.c.get('/app/profile/')
        self.assertEqual(response.status_code, 302)
        self.assertTemplateNotUsed(response, 'profile/view_profile.html')

        self.c.login(displayName=self.dn, password=self.p)
        response = self.c.get('/app/profile/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profile/view_profile.html')

        self.c.logout()
    
    def test_manage_profile(self):
        # should redirect if not logged in 
        response = self.c.get('/app/profile/manage/')
        self.assertEqual(response.status_code, 302)
        self.assertTemplateNotUsed(response, 'profile/manage_profile.html')

        self.c.login(displayName=self.dn, password=self.p)
        response = self.c.get('/app/profile/manage/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profile/manage_profile.html')

        self.c.logout()

    def test_view_other_user(self):
        other_user = User.objects.create_user(
            email='other@test.com',
            displayName='other',
            github='other',
            password=self.p,
            type='author'
        )

        self.c.login(displayName=self.dn, password=self.p)
        response = self.c.get(f'/app/profile/{other_user.id}')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profile/view_other_user.html')

        self.c.logout()

    def test_logout(self):
        self.c.login(displayName=self.dn, password=self.p)
        response = self.c.get('/app/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/index.html')

        self.c.get('/app/accounts/logout/')

        response = self.c.get('/app/')
        self.assertEqual(response.status_code, 302)
        self.assertTemplateNotUsed(response, 'app/index.html')