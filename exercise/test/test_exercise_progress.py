"""
This file is for testing the track exercise progress operation
- Classes:
    - ExerciseProgressTest: For creation related operations
- Helper functions:
    - create_user: creates a user and returns it
    - create_exercise: create an exercise with specific user and name
    - create_workout_log: create a workout_log with specific user
    - create_exercise_log: create an exercise log with
    - GET_EXERCISE_PROGRESS_URL: the url for the endpoint for
    tracking progress
- naming conventions:
    - test_...._suc: mean that the test is meant to success the operation
    it meant to do
    - test_...._error: mean that the test is meant to fail the operation
    it meant to do
"""
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from exercise.models import Exercise, ExerciseLog
from workout.models import WorkoutLog
EXERCISE_PROGRESS_URL = reverse('exercise:exercise-progress')


def create_user(email='test@gmail.com', password='test1234'):
    """Helper method to create a user"""
    return get_user_model().objects.create_user(email, password)


def create_exercise(name=None, user=None):
    """A helper method to create an exercise
    with certain user"""
    if not user:
        user = create_user(email='tst@gmail.com', password='test1234')
    return Exercise.objects.create(name=name, user=user)


def create_workout_log(user=None, name='default_name'):
    """Helper method to create a workoutlog"""
    return WorkoutLog.objects.create(user=user, name=name)


def create_exercise_log(user=None, exercise=None, workout=None, **kwargs):
    """A helper method to create an exercise log
    with certain user, workout and an exercise"""
    if not user:
        user = create_user(email='tst@gmail.com', password='test1234')
    return ExerciseLog.objects.create(exercise=exercise,
                                      user=user, workout_log=workout, **kwargs)


class ExerciseProgressTest(APITestCase):
    """
    Test class for testing the tracking progress feature for an exercise
    with its id in the parameters
    """

    def setUp(self):
        self.user = create_user()
        self.tmp_user = create_user(email='tmp@gmail.com')
        self.workout_log = create_workout_log(
            user=self.user, name='defaultWorkoutLog')
        self.exercise1 = create_exercise(name='exer1',
                                        user=self.user)
        self.exercise2 = create_exercise(name='exer2',
                                        user=self.user)
        self.exercise_tmp1 = create_exercise(name='exer1', user=self.tmp_user)
        self.client.force_authenticate(self.user)
        self.exer1_3 = create_exercise_log(user=self.user,
                                    exercise=self.exercise1,
                                    workout=self.workout_log,
                                    number_of_sets=31,
                                    number_of_reps=32,
                                    rest_between_sets_seconds=33,
                                    duration_in_minutes=34)
        self.exer1_1 = create_exercise_log(user=self.user,
                                    exercise=self.exercise1,
                                    workout=self.workout_log,
                                    number_of_sets=11,
                                    number_of_reps=12,
                                    rest_between_sets_seconds=13,
                                    duration_in_minutes=14)
        self.exer2_1 = create_exercise_log(user=self.user,
                                    exercise=self.exercise2,
                                    workout=self.workout_log,
                                    number_of_sets=211,
                                    number_of_reps=212,
                                    rest_between_sets_seconds=213,
                                    duration_in_minutes=214)
        self.exer1_2 = create_exercise_log(user=self.user,
                                    exercise=self.exercise1,
                                    workout=self.workout_log,
                                    number_of_sets=21,
                                    number_of_reps=22,
                                    rest_between_sets_seconds=23,
                                    duration_in_minutes=24)

    def assert_exercise_progress(self, exercise, progress, idx):
        """
        helper method to assert the info returned
        in the progress list for an exercise
        """
        self.assertEqual(exercise.number_of_reps,
                         progress[idx]['number_of_reps'])
        self.assertEqual(exercise.number_of_sets,
                         progress[idx]['number_of_sets'])
        self.assertEqual(exercise.rest_between_sets_seconds,
                         progress[idx]['rest_between_sets_seconds'])
        self.assertEqual(exercise.duration_in_minutes,
                         progress[idx]['duration_in_minutes'])

    def test_progress_with_nonauth_user_error(self):
        """
        Test ERROR: Retrieve a progress with an unauthinticated user
        """
        tmp_client = APIClient()
        res = tmp_client.get(EXERCISE_PROGRESS_URL,
                             {'exercise_id': self.exercise1.id})
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_track_progress_suc(self):
        """
        Test SUCCESS: Retrieve an exercise progress
        """
        res = self.client.get(EXERCISE_PROGRESS_URL,
                              {'exercise_id': str(self.exercise1.id)})
        self.assertEqual(self.exercise1.id, res.data['exercise_id'])
        self.assertEqual(self.exercise1.name, res.data['exercise_name'])
        progress = res.data['progress_logs']

        self.assert_exercise_progress(self.exer1_3, progress, 0)
        self.assert_exercise_progress(self.exer1_1, progress, 1)
        self.assert_exercise_progress(self.exer1_2, progress, 2)


    def test_track_progress_only_current_exercise_suc(self):
        """Test SUCCESS: the returned logs is this exercise's only """

        res = self.client.get(EXERCISE_PROGRESS_URL,
                              {'exercise_id': self.exercise2.id})
        self.assertEqual(self.exercise2.id, res.data['exercise_id'])
        self.assertEqual(self.exercise2.name, res.data['exercise_name'])
        progress = res.data['progress_logs']
        self.assertEqual(len(progress), 1)
        self.assert_exercise_progress(self.exer2_1, progress, 0)

    def test_try_track_other_user_exercise_not_found_error(self):
        """
        Test ERROR: try access other's user exercises progress
        """
        res = self.client.get(EXERCISE_PROGRESS_URL,
                              {'exercise_id': self.exercise_tmp1.id})
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_try_track_without_id_error(self):
        """
        Test Error: Try to track without specifying id
        """
        res = self.client.get(EXERCISE_PROGRESS_URL)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Exercise id is required.", res.data['Error'])

    def test_other_methods_not_allowed_error(self):
        """
        Test ERROR: access the endpoint with other method than get
        """
        res = self.client.post(EXERCISE_PROGRESS_URL,
                              {'exercise_id': self.exercise_tmp1.id})
        self.assertIn('Method "POST" not allowed.', res.data['detail'])

        res = self.client.patch(EXERCISE_PROGRESS_URL,
                              {'exercise_id': self.exercise_tmp1.id})
        self.assertIn('Method "PATCH" not allowed.', res.data['detail'])

        res = self.client.put(EXERCISE_PROGRESS_URL,
                              {'exercise_id': self.exercise_tmp1.id})
        self.assertIn('Method "PUT" not allowed.', res.data['detail'])

        res = self.client.delete(EXERCISE_PROGRESS_URL,
                              {'exercise_id': self.exercise_tmp1.id})
        self.assertIn('Method "DELETE" not allowed.', res.data['detail'])

    def test_track_progress_invalid_id_error(self):
        """
        Test ERROR: sendin an invalid error
        """
        res = self.client.get(EXERCISE_PROGRESS_URL,
                              {'exercise_id': ""})
        self.assertEqual(res.data['Error'], "Exercise id is required.")

        res = self.client.get(EXERCISE_PROGRESS_URL,
                              {'exercise_id': -2})
        self.assertEqual(res.data['Error'],
                         "Exercise ID must be a positive integer.")

        res = self.client.get(EXERCISE_PROGRESS_URL,
                              {'exercise_id': "Awab"})
        self.assertEqual(res.data['Error'],
                         "Exercise ID must be a valid integer.")

        res = self.client.get(EXERCISE_PROGRESS_URL,
                              {'exercise_id': 1.5})
        self.assertEqual(res.data['Error'],
                         "Exercise ID must be a valid integer.")
