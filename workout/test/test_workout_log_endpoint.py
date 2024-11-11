"""
This file is for testing the CRUD operation and basic
actions and constrains on the workoutlog endpoints
- Classes:
    - workoutLogsCreationTest: For creation related operations
    - WorkoutLogsRetrieveListTest: For retrieving-listing related operations
    - WorkoutLogsUpdateTest: For updating related operations
    - WorkoutLogsDeleteTest: For deleting related operations
- Helper functions:
    - GET_WORKOUT_LOG_DETAIL_URL: get the url for the endpoint responsibel for:
        - Retrieve
        - Update
        - Delete
    - create_user: creates a user and returns it
    - create_workoutLog: create a workoutlog with specific user
- static variables:
    - WORKOUT_LOG_LIST_CREATE_URL: the url for the endpoint for:
        - create a workout log
        - list all workout logs
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
from django.utils import timezone
from ..models import WorkoutLog, get_default_workout_log_name
WORKOUT_LOG_LIST_CREATE_URL = reverse('workout:workoutlog-list')


def GET_WORKOUT_LOG_DETAIL_URL(id):
    """Helper method to create the url to the endpoint responsible for:
    - Retrieve
    - delete
    - update"""
    return reverse("workout:workoutlog-detail", args=[id])


def create_user(email='test@gmail.com', password='test1234'):
    """Helper method to create a user"""
    return get_user_model().objects.create_user(email, password)


def create_workoutLog(name=None, user=None):
    """A helper method to create a workout log
    with certain user"""
    if not user:
        user = create_user(email='tst@gmail.com', password='test1234')
    return WorkoutLog.objects.create(name=name, user=user)


class workoutLogsCreationTest(TestCase):
    """A class for testing the creation operation
    of the workoutLog endpoints"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user()
        self.client.force_authenticate(self.user)

    def test_create_with_nonauth_user_error(self):
        """Test ERROR: creating a workout with an unauthinticated user"""
        tmp_client = APIClient()
        res = tmp_client.post(WORKOUT_LOG_LIST_CREATE_URL, {})
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_workout_suc(self):
        """Test SUCCESS: creating a workout with the current user"""
        res = self.client.post(WORKOUT_LOG_LIST_CREATE_URL, {})
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        # testing that the instance is being created in the database
        workout = WorkoutLog.objects.get(id=res.data['id'])
        self.assertEqual(workout.user, self.user)
        self.assertEqual(workout.name, get_default_workout_log_name())
        self.assertIsNone(workout.description)
        # testing create with description
        res = self.client.post(WORKOUT_LOG_LIST_CREATE_URL,
                               {'description': 'nnn'})
        workout = WorkoutLog.objects.get(id=res.data['id'])
        self.assertEqual(workout.description, 'nnn')

    def test_create_workout_with_start_workout_error(self):
        """Testing ERROR: creating a workout
        log with the start workout flag"""
        res = self.client.post(WORKOUT_LOG_LIST_CREATE_URL,
                               {'start_workout': True})
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        msg = 'start_workout and finish_workout can not be set on creating'
        self.assertIn(msg, res.data)

    def test_create_workout_with_finish_workout_error(self):
        """Testing ERROR: creating a workout
        log with the finish workout flag"""
        res = self.client.post(WORKOUT_LOG_LIST_CREATE_URL,
                               {'finish_workout': True})
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        msg = 'start_workout and finish_workout can not be set on creating'
        self.assertIn(msg, res.data)

    def test_create_workout_with_read_only_fields_error(self):
        """Testing ERROR: creating a workout log with a read_only_fields
        does not change the field, it just ignore it
        """
        tmp_time = timezone.now()
        res = self.client.post(WORKOUT_LOG_LIST_CREATE_URL, {
            'duration': tmp_time, 'created_at': True,
            'finished_at': tmp_time, 'started_at': tmp_time, 'id': 1000})
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data['duration'], None)
        self.assertNotEqual(res.data['created_at'], True)
        self.assertEqual(res.data['finished_at'], None)
        self.assertEqual(res.data['started_at'], None)
        self.assertNotEqual(res.data['id'], 1000)


class WorkoutLogsRetrieveListTest(TestCase):
    """A class for testing the retrieve operation
    of the workoutLog endpoints"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user()
        self.client.force_authenticate(self.user)

    def test_retrieve_with_nonauth_user_error(self):
        """Test ERROR: retrieving a workout with an unauthinticated user"""
        tmp_client = APIClient()
        create_workoutLog()
        res = tmp_client.get(GET_WORKOUT_LOG_DETAIL_URL(1))
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_with_nonauth_user_error(self):
        """Test ERROR: list workouts with an unauthinticated user"""
        tmp_client = APIClient()
        res = tmp_client.get(WORKOUT_LOG_LIST_CREATE_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_workout_log_suc(self):
        """Test SUCCESS: that the workout retrieved with all
        the fields and with details"""
        workout = create_workoutLog(user=self.user)
        URL = GET_WORKOUT_LOG_DETAIL_URL(workout.id)
        res = self.client.get(URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['name'], get_default_workout_log_name())
        self.assertIsNone(res.data['description'])
        self.assertIn('started_at', res.data)
        self.assertIn('finished_at', res.data)
        self.assertIn('created_at', res.data)
        self.assertIn('duration', res.data)

    def test_list_all_workout_logs_suc(self):
        """Test SUCCESS: listing all user workout logs"""
        workout1 = create_workoutLog(name='w1', user=self.user)
        workout2 = create_workoutLog(name='w2', user=self.user)
        res = self.client.get(WORKOUT_LOG_LIST_CREATE_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        ids = [workout['id'] for workout in res.data]
        self.assertIn(workout1.id, ids)
        self.assertIn(workout2.id, ids)

    def test_list_only_users_workout_logs_suc(self):
        """Test SUCCESS: that listing only returns user's workout logs
        not others"""
        my_workout = create_workoutLog(name='w1', user=self.user)
        user2 = create_user(email='tmp@gmail.com')
        other_workout = create_workoutLog(name='w2', user=user2)
        res = self.client.get(WORKOUT_LOG_LIST_CREATE_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        ids = [workout['id'] for workout in res.data]
        self.assertIn(my_workout.id, ids)
        self.assertNotIn(other_workout.id, ids)

    def test_list_return_no_details_suc(self):
        """Test SUCCESS: that listing does not return the
        details of the workout only the id, name, created_at"""
        create_workoutLog(name='w1', user=self.user)
        create_workoutLog(name='w2', user=self.user)
        res = self.client.get(WORKOUT_LOG_LIST_CREATE_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        for workout in res.data:
            self.assertNotIn('started_at', workout)
            self.assertNotIn('finished_at', workout)
            self.assertNotIn('duration', workout)
            self.assertNotIn('description', workout)
            self.assertIn('id', workout)
            self.assertIn('name', workout)
            self.assertIn('created_at', workout)


class WorkoutLogsUpdateTest(TestCase):
    """A class for testing the update related operation
    of the workoutLog endpoints"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user()
        self.client.force_authenticate(user=self.user)

    def test_update_with_nonauth_user_error(self):
        """Test ERROR: updating a workout with an unauthinticated user"""
        tmp_client = APIClient()
        create_workoutLog()
        payload = {
            'name': 'new name'
        }
        res = tmp_client.patch(GET_WORKOUT_LOG_DETAIL_URL(1), payload)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_partial_update_suc(self):
        """Test SUCCESS: parial update for a workout
        - update using put will be the same because
        if you don't have required fields, PUT and PATCH is the same"""
        workout = create_workoutLog(user=self.user)
        workout.description = 'old description'
        workout.save()
        URL = GET_WORKOUT_LOG_DETAIL_URL(workout.id)
        payload = {
            'name': 'new name',
        }
        res = self.client.patch(URL, payload)
        workout.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(workout.name, payload['name'])
        self.assertEqual(workout.description, 'old description')

    def test_update_user_error(self):
        """Testing ERROR: updating user is will not change anything"""
        workout = create_workoutLog(user=self.user)
        other_user = create_user(email='new@gmail.com')
        payload = {
            'user': other_user
        }
        URL = GET_WORKOUT_LOG_DETAIL_URL(workout.id)
        self.client.patch(URL, payload)
        res = self.client.get(WORKOUT_LOG_LIST_CREATE_URL)
        ids = [workout['id'] for workout in res.data]
        self.assertIn(workout.id, ids)

    def test_update_with_start_finish_together_error(self):
        """Test ERROR:
        update with providing the two flags start,finish together"""
        workout = create_workoutLog(user=self.user)
        URL = GET_WORKOUT_LOG_DETAIL_URL(workout.id)
        payload = {
            'start_workout': True,
            'finish_workout': True
        }
        res = self.client.patch(URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        error_msg = "You can't start and finish a workout at the same time"
        self.assertIn(error_msg, res.data)

    def test_update_with_finish_without_start_error(self):
        """Test ERROR: update with providing the finish flag without
         starting the workout atl all"""
        workout = create_workoutLog(user=self.user)
        URL = GET_WORKOUT_LOG_DETAIL_URL(workout.id)
        payload = {
            'finish_workout': True
        }
        res = self.client.patch(URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        error_msg = "You can't finish a workout without starting it"
        self.assertIn(error_msg, res.data)

    def test_update_with_start_twice_suc_error(self):
        """
        - Test SUCCESS: setting start workout
        - Test ERROR: update with providing the start flag after
        it was set before"""
        workout = create_workoutLog(user=self.user)
        URL = GET_WORKOUT_LOG_DETAIL_URL(workout.id)
        payload = {
            'start_workout': True
        }
        res = self.client.patch(URL, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(res.data['started_at'])
        payload = {
            'start_workout': True
        }
        res = self.client.patch(URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        error_msg = "You can't start a workout twice"
        self.assertIn(error_msg, res.data)

    def test_update_with_finish_twice(self):
        """
        - Test SUCCESS: setting finish workout
        after setting start workout
        - Test ERROR: update with providing the finish flag after
        it was set before"""
        workout = create_workoutLog(user=self.user)
        URL = GET_WORKOUT_LOG_DETAIL_URL(workout.id)
        payload = {
            'start_workout': True
        }
        self.client.patch(URL, payload)
        payload = {
            'finish_workout': True
        }
        res = self.client.patch(URL, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(res.data['finished_at'])
        payload = {
            'finish_workout': True
        }
        res = self.client.patch(URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        error_msg = "You can't finish a workout twice"
        self.assertIn(error_msg, res.data)


class WorkoutLogsDeleteTest(TestCase):
    """A class for testing the delete related operation
    of the workoutLog endpoints"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user()
        self.client.force_authenticate(user=self.user)

    def test_deleting_with_nonauth_user_error(self):
        """Test ERROR: deleting a workout with an unauthenticated user"""
        tmp_client = APIClient()
        create_workoutLog()
        res = tmp_client.delete(GET_WORKOUT_LOG_DETAIL_URL(1))
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_deleting_workout_log_suc(self):
        """Test SUCCESS: deleting a workout log"""
        workout = create_workoutLog(user=self.user)
        URL = GET_WORKOUT_LOG_DETAIL_URL(workout.id)
        res = self.client.delete(URL)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
