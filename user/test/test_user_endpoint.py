"""
Testing the endpoint for the user model
Public endpoints:
    - Creating User
Private endpoints:
    - Retrive User
    - Updating User
"""
from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient
from django.urls import reverse
from rest_framework import status
CREATE_USER_URL = reverse('user:create')
OBTAIN_TOKEN_URL = reverse('user:token_obtain')
GET_OR_UPDATE_URL = reverse('user:get_update')


def create_user(data):
    return get_user_model().objects.create_user(**data)


class PublicEndPointTest(TestCase):
    """A class for testing crud operation"""
    def setUp(self):
        self.client = APIClient()

    def test_create_user(self):
        """Testing creating user using endpoint"""
        payload = {
            'email': 'awabkhalid@gmail.com',
            'password': 'pass1234'
        }
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(email=payload['email'])
        self.assertTrue(user.check_password(payload['password']))

    def test_create_exist_user(self):
        """Testing creating existing user"""
        create_user({'email': 'exists@gmail.com',
                     'password': 'exists12345'})
        payload = {
            'email': 'exists@gmail.com',
            'password': 'pass1234'
        }
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_too_short_password(self):
        """Test creating user with a too short password"""
        payload = {
            'email': 'tooshort@gmail.com',
            'password': '234'
        }
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_obtaining_auth_token(self):
        """test for obtaining a token"""
        create_user({'email': 'obtaintoken@gmail.com',
                     'password': 'OB12345'})
        payload = {
            'email': 'obtaintoken@gmail.com',
            'password': 'OB12345'
        }
        res = self.client.post(OBTAIN_TOKEN_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('token', res.data)

    def test_obtaining_auth_token_with_password_whitspaces(self):
        create_user({'email': 'obp@gmail.com',
                     'password': 't12345'})
        payload = {
            'email': 'obp@gmail.com',
            'password': ' t12345  '
        }
        res = self.client.post(OBTAIN_TOKEN_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('token', res.data)

    def test_obtaining_auth_token_with_wrong_info(self):
        """test getting error for obtaining a token with wrong info"""
        payload = {
            'email': 'awab@gmail.com',
            'password': ' awab12345  '
        }
        res = self.client.post(OBTAIN_TOKEN_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('non_field_errors', res.data)
        # Check the specific error message format
        expected_message = 'The information you provided is not right'
        self.assertEqual(res.data['non_field_errors'][0], expected_message)

    def test_retrieve_unauth_user(self):
        """testing retreving a user with an unauthed user"""
        res = self.client.get(GET_OR_UPDATE_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_unauth_user(self):
        """testing retreving a user with an unauthed user"""
        payload = {
            'email': 'awab@gmail.com'
        }
        res = self.client.patch(GET_OR_UPDATE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateEndPointTest(TestCase):
    """Testing the private nedpoint for the User"""
    def setUp(self):
        self.client = APIClient()
        self.user = create_user({'email': 'awab@gmail.com',
                                 'password': 'awab1234'})
        self.client.force_authenticate(user=self.user)

    def test_retrieve_user(self):
        """Test retreving the data of a user"""
        res = self.client.get(GET_OR_UPDATE_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['email'], self.user.email)

    def test_post_not_allowed(self):
        """Test POST is not allowed for the retrieve_update endpoint"""
        res = self.client.post(GET_OR_UPDATE_URL)
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_updating_user(self):
        """Test updating all info for the user"""
        payload = {
            'email': 'awab2@gmail.com',
            'password': 'awab21234'
        }
        res = self.client.put(GET_OR_UPDATE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(self.user.email, payload['email'])
        self.assertTrue(self.user.check_password(payload['password']))

    def test_partial_updating_user(self):
        """Test updating partial info for the user"""
        payload = {
            'email': 'awab3@gmail.com'
        }
        res = self.client.patch(GET_OR_UPDATE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(self.user.email, payload['email'])

    def test_partial_with_put_error(self):
        """Test partial update with put method with cause error"""
        payload = {
            'email': 'awab3@gmail.com'
        }
        res = self.client.put(GET_OR_UPDATE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotEqual(self.user.email, payload['email'])
