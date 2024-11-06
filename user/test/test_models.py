"""
This file is for testing the model related operations
for the User model
- Classes:
    - UserModelsTests: for the related operations of User model
- naming conventions:
    - test_...._suc: mean that the test is meant to success the operation
    it meant to do
    - test_...._error: mean that the test is meant to fail the operation
    it meant to do
"""
from django.test import TestCase
from django.contrib.auth import get_user_model


class UserModelsTests(TestCase):
    """Testing the model operations of User model"""
    def test_create_user_suc(self):
        """Test SUCCESS: For creating user"""
        tmp_user = {'email': "awab@gmail.com", 'password': "1234"}
        user = get_user_model().objects.\
            create_user(email=tmp_user['email'],
                        password=tmp_user['password'])
        self.assertEqual(user.email, tmp_user['email'])
        self.assertTrue(user.check_password(tmp_user['password']))

    def test_create_superuser_suc(self):
        """Test SUCCESS: For creating user"""
        tmp_user = {'email': "awab@gmail.com", 'password': "1234"}
        user = get_user_model().objects.\
            create_superuser(email=tmp_user['email'],
                             password=tmp_user['password'])
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)

    def test_email_norm_suc(self):
        """Test SUCCESS: For normalizing email"""
        email = 'AWAB@GMAIL.COM'
        user = get_user_model().objects.create_user(email=email,
                                                    password="1234")
        self.assertEqual(user.email, email.lower())

    def test_empty_email_error(self):
        """Test ERROR: for inserting empty email"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(email="", password="1234")

    def test_invalid_email_error(self):
        """Test ERROR: for inserting invalid email"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(email="Awabgmail.com",
                                                 password="1234")
