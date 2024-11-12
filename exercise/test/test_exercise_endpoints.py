"""
This file is for testing the CRUD operation and basic
actions and constrains on the Exercise endpoints
- Classes:
    - ExerciseCreationTest: For creation related operations
    - ExerciseRetrieveListTest: For retrieving-listing related operations
    - ExerciseUpdateTest: For updating related operations
    - ExerciseDeleteTest: For deleting related operations
- Helper functions:
    - GET_EXERCISE_DETAIL_URL: get the url for the endpoint responsible for:
        - Retrieve
        - Update
        - Delete
    - create_user: creates a user and returns it
    - create_exercise: create an exercise with specific user and name
- static variables:
    - EXERCISE_LIST_CREATE_URL: the url for the endpoint for:
        - create an exercise
        - list all exercises
- naming conventions:
    - test_...._suc: mean that the test is meant to success the operation
    it meant to do
    - test_...._error: mean that the test is meant to fail the operation
    it meant to do
"""
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from django.test import TestCase
from django.urls import reverse
from exercise.models import Exercise
EXERCISE_LIST_CREATE_URL = reverse('exercise:exercise-list')


def GET_EXERCISE_DETAIL_URL(id):
    """Helper method to create the url to the endpoint responsible for:
    - Retrieve
    - delete
    - update"""
    return reverse("exercise:exercise-detail", args=[id])


def create_user(email='test@gmail.com', password='test1234'):
    """Helper method to create a user"""
    return get_user_model().objects.create_user(email, password)


def create_exercise(name=None, user=None):
    """A helper method to create an exercise
    with certain user"""
    if not user:
        user = create_user(email='tst@gmail.com', password='test1234')
    return Exercise.objects.create(name=name, user=user)


class ExerciseCreationTest(TestCase):
    """A class for testing the creation operation
    of the Exercise endpoints"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user()
        self.client.force_authenticate(self.user)
        self.tmp_user = create_user(email="testtmp@gmail.com")
        self.exercise = create_exercise(name="defaultName", user=self.user)

    def test_create_exercise_with_nonauth_user_error(self):
        """Test ERROR: creating an exercise with an unauthinticated user"""
        tmp_client = APIClient()
        res = tmp_client.post(EXERCISE_LIST_CREATE_URL, {'name': "exer1"})
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_exercise_suc(self):
        """Test SUCCESS: creating an exercise with the current user"""
        res = self.client.post(EXERCISE_LIST_CREATE_URL, {'name': "exer1"})
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        # testing that the instance is being created in the database
        exercise = Exercise.objects.get(id=res.data['id'])
        self.assertEqual(exercise.user, self.user)
        self.assertIsNone(exercise.description)
        # testing create with notes
        res = self.client.post(EXERCISE_LIST_CREATE_URL,
                               {'name': 'test',
                                'description':  'desc1'})
        exercise = Exercise.objects.get(id=res.data['id'])
        self.assertEqual(exercise.description, 'desc1')

    def test_create_exercise_without_name_error(self):
        """Test ERROR: creating an exercise without the name"""
        res = self.client.post(EXERCISE_LIST_CREATE_URL)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_exercise_empty_name_error(self):
        """Test ERROR: creating an exercise with an empty name"""
        res = self.client.post(EXERCISE_LIST_CREATE_URL, {'name': ''})
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_exercise_with_user_error(self):
        """Test ERROR: creating an exercise with giving user in  the request
        will not effect anything will create with the current user"""
        res = self.client.post(EXERCISE_LIST_CREATE_URL,
                               {'name': 'test', 'user': self.tmp_user})
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data['user'], self.user.id)

    def test_create_exercise_with_case_insensitive_error(self):
        """Test ERROR: the case insensitive feature for
        the name of the exercise"""
        res = self.client.post(EXERCISE_LIST_CREATE_URL,
                               {'name': 'dEfAultname', 'user': self.user})
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        msg = "An exercise with the name 'dEfAultname' already exists."
        self.assertIn(msg, res.data['name'])

    def test_create_exercise_name_case_insensitive_diff_user_suc(self):
        """Test SUCCESS: the case insensitive feature for
        the name of the exercise"""
        tmp_user = create_user(email='e@gmail.com')
        client = APIClient()
        client.force_authenticate(tmp_user)
        res = client.post(EXERCISE_LIST_CREATE_URL, {'name': 'defaultName',
                                                     'user': tmp_user})
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data['user'], tmp_user.id)
        tmp_user.delete()


class ExerciseRetrieveListTest(TestCase):
    """A class for testing the retrieve operation
    of the Exercise endpoints"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user()
        self.client.force_authenticate(self.user)
        self.tmp_user = create_user(email="testtmp@gmail.com")
        self.exercise = create_exercise(name="defaultName", user=self.user)

    def test_retrieve_with_nonauth_user_error(self):
        """Test ERROR: retrieving an exercise with an unauthinticated user"""
        tmp_client = APIClient()
        tmpexer = create_exercise(name='tmp')
        res = tmp_client.get(GET_EXERCISE_DETAIL_URL(tmpexer.id))
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        tmpexer.delete()

    def test_list_with_nonauth_user_error(self):
        """Test ERROR: list exercises with an unauthinticated user"""
        tmp_client = APIClient()
        res = tmp_client.get(EXERCISE_LIST_CREATE_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_exercise_suc(self):
        """Test SUCCESS: that the exercise retrieved with all
        the fields and with details"""
        URL = GET_EXERCISE_DETAIL_URL(self.exercise.id)
        res = self.client.get(URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['name'], 'defaultName')
        self.assertEqual(res.data['user'], self.user.id)
        self.assertIsNone(res.data['description'])

    def test_list_all_exercises_suc(self):
        """Test SUCCESS: listing all user exercises"""
        exer1 = create_exercise(name='e1', user=self.user)
        exer2 = create_exercise(name='e2', user=self.user)
        res = self.client.get(EXERCISE_LIST_CREATE_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        ids = [exer['id'] for exer in res.data]
        self.assertIn(exer1.id, ids)
        self.assertIn(exer2.id, ids)
        exer1.delete()
        exer2.delete()

    def test_list_only_users_exercises_suc(self):
        """Test SUCCESS: that listing only returns user's exercises
        not others"""
        other_exercise = create_exercise(name='e2', user=self.tmp_user)
        res = self.client.get(EXERCISE_LIST_CREATE_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        ids = [exercise['id'] for exercise in res.data]
        self.assertIn(self.exercise.id, ids)
        self.assertNotIn(other_exercise.id, ids)
        other_exercise.delete()

    def test_list_return_no_details_suc(self):
        """Test SUCCESS: that listing does not return the
        details of the exercise only the id, name"""
        res = self.client.get(EXERCISE_LIST_CREATE_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        for exer in res.data:
            self.assertNotIn('description', exer)
            self.assertIn('id', exer)
            self.assertIn('name', exer)


class ExerciseUpdateTest(TestCase):
    """A class for testing the update related operation
    of the workoutLog endpoints"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user()
        self.client.force_authenticate(self.user)
        self.tmp_user = create_user(email="testtmp@gmail.com")
        self.exercise = create_exercise(name="defaultName", user=self.user)

    def test_update_with_nonauth_user_error(self):
        """Test ERROR: updating an exercise with an unauthinticated user"""
        tmp_client = APIClient()
        payload = {
            'name': 'new name'
        }
        res = tmp_client.patch(
            GET_EXERCISE_DETAIL_URL(self.exercise.id), payload)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_partial_update_suc(self):
        """Test SUCCESS: parial update for an exercise"""
        self.exercise.description = 'old description'
        self.exercise.save()
        URL = GET_EXERCISE_DETAIL_URL(self.exercise.id)
        old_name = self.exercise.name
        payload = {
            'name': 'new name',
        }
        res = self.client.patch(URL, payload)
        self.exercise.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(self.exercise.name, payload['name'])
        self.assertEqual(self.exercise.description, 'old description')
        self.exercise.name = old_name
        self.exercise.save()

    def test_full_update_suc(self):
        """Test SUCCESS: trying to update all fields
         """
        self.exercise.description = 'old description'
        self.exercise.save()
        URL = GET_EXERCISE_DETAIL_URL(self.exercise.id)
        old_name = self.exercise.name
        payload = {
            'name': 'new name',
            'description': 'new description',
        }
        res = self.client.put(URL, payload)
        self.exercise.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(self.exercise.name, 'new name')
        self.assertEqual(self.exercise.description, 'new description')
        self.exercise.name = old_name
        self.exercise.save()

    def test_full_update_not_all_required_fields__error(self):
        """Test ERROR: trying to update with put method without
         providing all the required field update for an exercise
         """
        self.exercise.description = 'old description'
        self.exercise.save()
        URL = GET_EXERCISE_DETAIL_URL(self.exercise.id)
        old_name = self.exercise.name
        payload = {
            'description': 'new description',
        }
        res = self.client.put(URL, payload)
        self.exercise.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(self.exercise.name, old_name)
        self.assertNotEqual(self.exercise.description, 'new description')
        self.assertEqual(self.exercise.description, 'old description')

    def test_update_user_error(self):
        """Testing ERROR: updating user is will not change anything"""
        payload = {
            'user': self.tmp_user
        }
        URL = GET_EXERCISE_DETAIL_URL(self.exercise.id)
        self.client.patch(URL, payload)
        res = self.client.get(EXERCISE_LIST_CREATE_URL)
        ids = [exer['id'] for exer in res.data]
        self.assertIn(self.exercise.id, ids)

    def test_update_name_with_case_insensitive_error(self):
        """Testing ERROR: updating the name with
        existing name but different case"""
        tmp_exercise = create_exercise(name='oldname', user=self.user)
        payload = {
            'name': 'DefauLtNAME'
        }
        URL = GET_EXERCISE_DETAIL_URL(tmp_exercise.id)
        res = self.client.patch(URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        tmp_exercise.refresh_from_db()
        self.assertEqual(tmp_exercise.name, 'oldname')
        tmp_exercise.delete()

    def test_update_name_with_the_same_name_suc(self):
        """Test SUCCESS: update an exercise with the same name"""
        URL = GET_EXERCISE_DETAIL_URL(self.exercise.id)
        payload = {
            'name': self.exercise.name
        }
        res = self.client.patch(URL, payload)
        self.exercise.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['name'], self.exercise.name)


class ExerciseDeleteTest(TestCase):
    """A class for testing the delete related operation
    of the Exercise endpoints"""
    def setUp(self):
        self.client = APIClient()
        self.user = create_user()
        self.client.force_authenticate(self.user)
        self.tmp_user = create_user(email="testtmp@gmail.com")
        self.exercise = create_exercise(name="defaultName", user=self.user)

    def test_deleting_with_nonauth_user_error(self):
        """Test ERROR: deleting an exercise with an unauthenticated user"""
        tmp_client = APIClient()
        exr = create_exercise(name='tmp', user=self.user)
        res = tmp_client.delete(GET_EXERCISE_DETAIL_URL(exr.id))
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_deleting_workout_log_suc(self):
        """Test SUCCESS: deleting an exercise"""
        URL = GET_EXERCISE_DETAIL_URL(self.exercise.id)
        res = self.client.delete(URL)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
