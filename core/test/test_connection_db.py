"""Test connection with the database"""
from django.test import TestCase
from django.db import connection


class ConnectionTest(TestCase):
    """Test the connection with the databas"""
    def test_connection(self):
        """Test the connection"""
        try:
            connection.ensure_connection()
            self.assertTrue(connection.is_usable())
        except Exception as e:
            self.fail(f"Database connection failed: {e}")
