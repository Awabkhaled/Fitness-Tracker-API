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

    def test_progress_with_nonauth_user_error(self):
        """
        Test ERROR: Retrieve a progress with an unauthinticated user
        """
        tmp_client = APIClient()
        res = tmp_client.get(EXERCISE_PROGRESS_URL,
                             {'exercise_id': self.exercise1.id})
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_track_progress_sets_reps_rest_suc(self):
        """
        Test SUCCESS: Retrieve an exercise progress,
        testing sets reps returned values
        """
        sets = [2, 3, 4, 4, 4, 4, 4, None, 12, 10,
                13, 13, 13, 13, 13, 13, 13, 13]

        reps = [1, 1, 1, 5, 6, 6, 6, None, None, 2,
                None, None, None, 2, 2, 2, 2, 2]

        rest = [30, 30, 60, 60, 6, 10, 20, None, 10, None,
                None, 12, None, None, 1, 1, None, 2]

        expected_sets_output = [(2, 1, 30), (3, 1, 30), (4, 1, 60),
                                (4, 5, 60), (4, 6, 6), (4, 6, 10),
                                (4, 6, 20), (12, None, 10), (10, 2, None),
                                (13, None, None), (13, None, 12),
                                (13, 2, None), (13, 2, 1), (13, 2, 2)]
        expected_counter_output = [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 2]
        for i in range(len(sets)):
            create_exercise_log(user=self.user, exercise=self.exercise1,
                                workout=self.workout_log,
                                number_of_sets=sets[i],
                                number_of_reps=reps[i],
                                rest_between_sets_seconds=rest[i])
        res = self.client.get(EXERCISE_PROGRESS_URL,
                              {'exercise_id': self.exercise1.id})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(self.exercise1.id, res.data['exercise_id'])
        self.assertEqual(self.exercise1.name, res.data['exercise_name'])
        progress = res.data['progress']
        expected_keys = ['sets_reps_restTime',
                         'number_exercises_between_each_sets_reps_restTime']
        self.assertEqual(expected_keys, list(progress.keys()))
        sets_progress = progress['sets_reps_restTime']
        for i in range(len(expected_sets_output)):
            self.assertEqual(sets_progress[i][0], expected_sets_output[i])
            self.assertEqual(sets_progress[i][2], self.workout_log.id)
        counts_progress = \
            progress['number_exercises_between_each_sets_reps_restTime']
        for i in range(len(expected_counter_output)):
            self.assertEqual(counts_progress[i], expected_counter_output[i])

    def test_track_progress_only_user_exercise_suc(self):
        """
        Test SUCCESS: Retrieve an exercise progress, it only retrieve the user
        and exercise sppecified
        """
        sets = [2, 3, 4, 4, 4, 4, 4, None, 12, 10, 13]
        reps = [1, 1, 1, 5, 6, 6, 6, None, None, 2, None]
        rest = [30, 30, 60, 60, 6, 10, 20, None, 10, None, None]
        expected_sets_output = [(2, 1, 30), (3, 1, 30), (4, 1, 60),
                                (4, 5, 60), (4, 6, 6), (4, 6, 10),
                                (4, 6, 20), (12, None, 10), (10, 2, None),
                                (13, None, None)]
        expected_counter_output = [0, 0, 0, 0, 0, 0, 1, 0, 0]
        for i in range(len(sets)):
            create_exercise_log(user=self.user, exercise=self.exercise1,
                                workout=self.workout_log,
                                number_of_sets=sets[i],
                                number_of_reps=reps[i],
                                rest_between_sets_seconds=rest[i])
            create_exercise_log(user=self.user, exercise=self.exercise2,
                                workout=self.workout_log,
                                number_of_sets=sets[i],
                                number_of_reps=reps[i],
                                rest_between_sets_seconds=rest[i])
            create_exercise_log(user=self.tmp_user, exercise=self.exercise2,
                                workout=self.workout_log,
                                number_of_sets=sets[i],
                                number_of_reps=reps[i],
                                rest_between_sets_seconds=rest[i])
        res = self.client.get(EXERCISE_PROGRESS_URL,
                              {'exercise_id': self.exercise1.id})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(self.exercise1.id, res.data['exercise_id'])
        self.assertEqual(self.exercise1.name, res.data['exercise_name'])
        progress = res.data['progress']
        expected_keys = ['sets_reps_restTime',
                         'number_exercises_between_each_sets_reps_restTime']
        self.assertEqual(expected_keys, list(progress.keys()))
        sets_progress = progress['sets_reps_restTime']
        for i in range(len(expected_sets_output)):
            self.assertEqual(sets_progress[i][0], expected_sets_output[i])
            self.assertEqual(sets_progress[i][2], self.workout_log.id)
        counts_progress = \
            progress['number_exercises_between_each_sets_reps_restTime']
        for i in range(len(expected_counter_output)):
            self.assertEqual(counts_progress[i], expected_counter_output[i])

    def test_track_progress_other_fields_suc(self):
        """
        Test SUCCESS: Retrieve an exercise progress, it only retrieve the user
        and exercise sppecified, and testing other fields
        """
        duration = [30, 12, 50, 60, 10, None, None, 1, 1, 1, 1, 2]
        weight_in_kg = [300, 500, 10, 0, 10, None, None, 1, 1, 1, 1, 2]
        expected_counter_output = [0, 0, 0, 0, 2, 3]
        expected = {
            'weight_in_kg': [300, 500, 10, 0, 10, 1, 2],
            'duration_in_minutes': [30, 12, 50, 60, 10, 1, 2]
        }
        for i in range(len(duration)):
            create_exercise_log(user=self.user, exercise=self.exercise1,
                                workout=self.workout_log,
                                duration_in_minutes=duration[i],
                                weight_in_kg=weight_in_kg[i])
            create_exercise_log(user=self.user, exercise=self.exercise2,
                                workout=self.workout_log,
                                duration_in_minutes=duration[i])
            create_exercise_log(user=self.tmp_user, exercise=self.exercise2,
                                workout=self.workout_log,
                                duration_in_minutes=duration[i])
        res = self.client.get(EXERCISE_PROGRESS_URL,
                              {'exercise_id': self.exercise1.id})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(self.exercise1.id, res.data['exercise_id'])
        self.assertEqual(self.exercise1.name, res.data['exercise_name'])
        progress = res.data['progress']
        expected_keys = ['duration_in_minutes',
                         'number_exercises_between_each_duration_in_minutes',
                         'weight_in_kg',
                         'number_exercises_between_each_weight_in_kg']
        self.assertEqual(expected_keys, list(progress.keys()))
        fields = ['duration_in_minutes', 'weight_in_kg']
        for field in fields:
            field_progress = progress[f'{field}']
            for i in range(len(expected[f'{field}'])):
                self.assertEqual(field_progress[i][0], expected[f'{field}'][i])
                self.assertEqual(field_progress[i][2], self.workout_log.id)

            counts_progress = \
                progress[f'number_exercises_between_each_{field}']
            for i in range(len(expected_counter_output)):
                self.assertEqual(counts_progress[i],
                                 expected_counter_output[i])

    def test_track_progress_all_fields_suc(self):
        """
        Test SUCCESS: Retrieve an exercise progress using all fields
        """
        duration = [30, 12, 50, 60, 10, None, None,
                    1, 1, 1, 1, 2, 2, 2, 2, 2, 3, 4]
        weight_in_kg = [300, 500, 10, 0, 10, None,
                        None, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 5]
        sets = [2, 3, 4, 4, 4, 4, 4, None, 12, 10,
                13, 13, 13, 13, 13, 13, 13, 13]
        reps = [1, 1, 1, 5, 6, 6, 6, None, None, 2,
                None, None, None, 2, 2, 2, 2, 2]
        rest = [30, 30, 60, 60, 6, 10, 20, None, 10, None,
                None, 12, None, None, 1, 1, None, 2]
        expected = {
            'weight_in_kg': [300, 500, 10, 0, 10, 1, 2, 5],
            'duration_in_minutes': [30, 12, 50, 60, 10, 1, 2, 3, 4],
            'sets_reps_restTime': [(2, 1, 30), (3, 1, 30), (4, 1, 60),
                                   (4, 5, 60), (4, 6, 6), (4, 6, 10),
                                   (4, 6, 20), (12, None, 10), (10, 2, None),
                                   (13, None, None), (13, None, 12),
                                   (13, 2, None), (13, 2, 1), (13, 2, 2)]
        }
        expected_counter = {
            'weight_in_kg': [0, 0, 0, 0, 2, 3, 5],
            'duration_in_minutes': [0, 0, 0, 0, 2, 3, 4, 0],
            'sets_reps_restTime': [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 2]
        }
        for i in range(len(duration)):
            create_exercise_log(user=self.user, exercise=self.exercise1,
                                workout=self.workout_log,
                                duration_in_minutes=duration[i],
                                weight_in_kg=weight_in_kg[i],
                                number_of_sets=sets[i],
                                number_of_reps=reps[i],
                                rest_between_sets_seconds=rest[i])
        res = self.client.get(EXERCISE_PROGRESS_URL,
                              {'exercise_id': self.exercise1.id})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(self.exercise1.id, res.data['exercise_id'])
        self.assertEqual(self.exercise1.name, res.data['exercise_name'])
        progress = res.data['progress']
        expected_keys = ['duration_in_minutes',
                         'number_exercises_between_each_duration_in_minutes',
                         'weight_in_kg',
                         'number_exercises_between_each_weight_in_kg',
                         'sets_reps_restTime',
                         'number_exercises_between_each_sets_reps_restTime']
        self.assertEqual(expected_keys, list(progress.keys()))
        fields = ['duration_in_minutes', 'weight_in_kg', 'sets_reps_restTime']
        for field in fields:
            field_progress = progress[f'{field}']
            for i in range(len(expected[f'{field}'])):
                self.assertEqual(field_progress[i][0], expected[f'{field}'][i])
                self.assertEqual(field_progress[i][2], self.workout_log.id)

            counts_progress = \
                progress[f'number_exercises_between_each_{field}']
            for i in range(len(expected_counter[f'{field}'])):
                self.assertEqual(counts_progress[i],
                                 expected_counter[f'{field}'][i])

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

    def test_progress_no_progress_suc(self):
        """
        Test SUCCESS: Retrieve an exercise progress, but with no progress
        """
        res = self.client.get(EXERCISE_PROGRESS_URL,
                              {'exercise_id': str(self.exercise1.id)})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(self.exercise1.id, res.data['exercise_id'])
        self.assertEqual(self.exercise1.name, res.data['exercise_name'])
        self.assertEqual(len(res.data['progress']), 0)

    def test_progress_mixed_counter_suc(self):
        """
        Test SUCCESS: Retrieve an exercise progress, but with only one
        progress in some fields and other more that one.
        """
        duration = [0, 1, 1]
        weight_in_kg = [0, 0, None]
        sets = [2, 2, 2]
        reps = [1, 1, 1]
        rest = [30, 30, 30]
        expected = {
            'weight_in_kg': [0],
            'duration_in_minutes': [0, 1],
            'sets_reps_restTime': [(2, 1, 30)]
        }
        duration_in_minutes_counter = [0]

        for i in range(len(duration)):
            create_exercise_log(user=self.user, exercise=self.exercise1,
                                workout=self.workout_log,
                                duration_in_minutes=duration[i],
                                weight_in_kg=weight_in_kg[i],
                                number_of_sets=sets[i],
                                number_of_reps=reps[i],
                                rest_between_sets_seconds=rest[i])
        res = self.client.get(EXERCISE_PROGRESS_URL,
                              {'exercise_id': str(self.exercise1.id)})
        progress = res.data['progress']
        expected_keys = ['duration_in_minutes',
                         'number_exercises_between_each_duration_in_minutes',
                         'weight_in_kg',
                         'number_exercises_between_each_weight_in_kg',
                         'sets_reps_restTime',
                         'number_exercises_between_each_sets_reps_restTime']
        self.assertEqual(expected_keys, list(progress.keys()))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(self.exercise1.id, res.data['exercise_id'])
        self.assertEqual(self.exercise1.name, res.data['exercise_name'])
        self.assertEqual(0, len(
            progress['number_exercises_between_each_weight_in_kg']))
        self.assertEqual(0, len(
            progress['number_exercises_between_each_sets_reps_restTime']))
        fields = ['duration_in_minutes', 'weight_in_kg', 'sets_reps_restTime']
        for field in fields:
            field_progress = progress[f'{field}']
            for i in range(len(expected[f'{field}'])):
                self.assertEqual(field_progress[i][0], expected[f'{field}'][i])
                self.assertEqual(field_progress[i][2], self.workout_log.id)
        counts_progress = \
            progress['number_exercises_between_each_duration_in_minutes']
        for i in range(len(counts_progress)):
            self.assertEqual(counts_progress[i],
                             duration_in_minutes_counter[i])
