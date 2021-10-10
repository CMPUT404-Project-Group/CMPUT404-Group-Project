from django.test import TestCase
from rest_framework.test import APIClient
from django.urls import reverse
from .models import User
from urllib.parse import quote, uses_fragment

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
