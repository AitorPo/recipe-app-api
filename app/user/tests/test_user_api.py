from django.test import TestCase
from django.contrib.auth import get_user_model
# reverse is for generating api urls
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

# this is a constant. that's why we write it uppercase
CREATE_USER_URL = reverse('user:create')
# line above create the url assigned to create a new user
TOKEN_URL = reverse('user:token')


def create_user(**params):
    return get_user_model().objects.create_user(**params)


# public api refers to an unauthenticated user. AKA guests
class PublicUserApiTests(TestCase):
    """Test the users API (public/guests)"""

    def setUp(self):
        self.client = APIClient()

    def test_create_valid_user_success(self):
        """Test creating user with valid payload is succsessful"""
        # payload = object we pass through the API to create a new db object
        payload = {
            'email': 'test@correo.com',
            'password': 'testpass',
            'name': 'Test name'
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(**res.data)
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)

    def test_user_exists(self):
        """Test creating a user that already exists fails"""
        payload = {
            'email': 'test@correo.com',
            'password': 'testpass',
            'name': 'Test name'
        }
        # ** makes this: it passes attr in our dict equaling key to value
        # i.e. => email = test@correo.com
        create_user(**payload)

        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """Test that the password must be more than 5 characters"""
        payload = {
            'email': 'test@correo.com',
            'password': 'pw',
            'name': 'Test'
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exists)

    # Auth tests
    def test_create_token_for_user(self):
        """Test that a token is created for the user"""
        payload = {'email': 'test@correo.com', 'password': 'testpass'}
        create_user(**payload)
        res = self.client.post(TOKEN_URL, payload)

        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_invalid_credentials(self):
        """Test that token is not created and invalid credentials are given"""
        create_user(email='test@correo.com', password='testpass')
        payload = {'email': 'test@correo.com', 'password': 'wrong'}
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_no_user(self):
        """Test that token is not created if user doesn't exist"""
        # We don't need to worry about users created in previous tests
        # because we reset the db every time we launch a test in our cmd
        # so each test is isolated from the others
        payload = {'email': 'test@correo.com', 'password': 'testpass'}
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_missing_field(self):
        """Test that email and password are required"""
        res = self.client.post(TOKEN_URL, {'email': 'one', 'password': ''})
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
