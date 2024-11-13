"""
This file is for testing the search operations on the exercises
- Classes:
    - ExerciseFieldSearchTest: For creation related operations
- Helper functions:
    - create_user: creates a user and returns it
    - create_exercise: create an exercise with specific user and name
- static variables:
    - EXERCISE_PARAM_SEARCH_URL: the url for the endpoint for
    searching an exercise with a certain field value using parameters
- naming conventions:
    - test_...._suc: mean that the test is meant to success the operation
    it meant to do
    - test_...._error: mean that the test is meant to fail the operation
    it meant to do
"""
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from exercise.models import Exercise
EXERCISE_FIELDS_SEARCH_URL = reverse('exercise:exercise-search')


def create_user(email='test@gmail.com', password='test1234'):
    """Helper method to create a user"""
    return get_user_model().objects.create_user(email, password)


def create_exercise(name=None, user=None, **kwargs):
    """A helper method to create an exercise with certain user"""
    if not user:
        user = create_user(email='tst@gmail.com', password='test1234')
    return Exercise.objects.create(name=name, user=user, **kwargs)


class ExerciseFieldSearchTest(APITestCase):
    """
    Test class for testing the searching feature for an exercise
    with its field using params
    """

    def setUp(self):
        self.user = create_user()
        self.client.force_authenticate(self.user)
        create_exercise("push up", self.user,
                        description="push up desc")
        create_exercise("push down", self.user,
                        description="push down desc")
        create_exercise("pull up", self.user,
                        description="pull up desc")
        create_exercise("pull down", self.user,
                        description="pull down desc")
        create_exercise("regular bench press", self.user,
                        description="regular bench desc")
        create_exercise("incline bench press", self.user,
                        description="incline bench desc")

    def test_search_by_name_suc(self):
        """
        Test SUCCESS: search an exercise by name
        - should return exercise that has name that contain the search value
        """
        search_name = "push"
        res = self.client.get(EXERCISE_FIELDS_SEARCH_URL,
                              {'name': search_name})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 2)
        # make sure that it returns name and id
        exercises_name = [exer['name'] for exer in res.data]
        self.assertIn('push up', exercises_name)
        self.assertIn('push down', exercises_name)
        push_up_id = Exercise.objects.get_CI(name='push up').id
        push_down_id = Exercise.objects.get_CI(name='push down').id
        exercises_ids = [exer['id'] for exer in res.data]
        self.assertIn(push_down_id, exercises_ids)
        self.assertIn(push_up_id, exercises_ids)

    def test_search_and_return_only_user_suc(self):
        """
        Test SUCCESS: searching an exercise only return users
        """
        new_exercise = create_exercise(
            'push down', user=create_user(email='tmp@gmail.com'))
        exers = Exercise.objects.filter_CI(name='push down')
        self.assertEqual(len(exers), 2)
        search_name = "push down"
        res = self.client.get(EXERCISE_FIELDS_SEARCH_URL,
                              {'name': search_name})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        exercises_ids = [exer['id'] for exer in res.data]
        self.assertNotIn(new_exercise.id, exercises_ids)

    def test_search_by_name_case_insensitive_suc(self):
        """
        Test SUCCESS: search an exercise by name case insensitive
        - should return exercise that has name that contain the search value
        """
        search_name = " pULl "
        res = self.client.get(EXERCISE_FIELDS_SEARCH_URL,
                              {'name': search_name})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 2)
        exercises_name = [exer['name'] for exer in res.data]
        self.assertIn('pull up', exercises_name)
        self.assertIn('pull down', exercises_name)

    def test_search_by_name_empty_error(self):
        """
        Test ERROR: search an exercise by empty name
        - should not return anything
        """
        search_name = ""
        res = self.client.get(EXERCISE_FIELDS_SEARCH_URL,
                              {'name': search_name})
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Parameters empty or invalid", res.data)

    def test_search_with_no_params_error(self):
        """
        Test ERROR: search an exercise with nothing
        - note: will not return anything
        """
        res = self.client.get(EXERCISE_FIELDS_SEARCH_URL, {})
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Parameters empty or invalid", res.data)

    def test_search_with_strange_params_error(self):
        """
        Test ERROR: search an exercise with params
        that is not used in searching
        - note: will not return anything
        """
        res = self.client.get(EXERCISE_FIELDS_SEARCH_URL,
                              {'test': 'test1', 'bool': True})
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Parameters empty or invalid", res.data)
