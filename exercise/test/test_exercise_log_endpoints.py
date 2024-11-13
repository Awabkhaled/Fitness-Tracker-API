"""
This file is for testing the CRUD operation and basic
actions and constrains on the Exercise endpoints
- Classes:
    - ExerciseLogCreationTest: For creation related operations
    - ExerciseLogRetrieveListTest: For retrieving-listing related operations
    - ExerciseLogUpdateTest: For updating related operations
    - ExerciseLogDeleteTest: For deleting related operations
- Helper functions:
    - GET_EXERCISE_LOG_DETAIL_URL: get url for the endpoint responsible for:
        - Retrieve
        - Update
        - Delete
    - create_user: creates a user and returns it
    - create_exercise: create an exercise with specific user and name
    - create_workout_log: create a workout_log with specific user
    - create_exercise_log: create an exercise log with
    specific user, workout, exercise
- static variables:
    - EXERCISE_LOG_LIST_CREATE_URL: the url for the endpoint for:
        - create an exercise log
        - list all exercise logs
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
from exercise.models import (
    Exercise,
    ExerciseLog
)
from workout.models import WorkoutLog
EXERCISE_LOG_LIST_CREATE_URL = reverse('exercise:exerciselog-list')


def GET_EXERCISE_LOG_DETAIL_URL(id):
    """Helper method to create the url to the endpoint responsible for:
    - Retrieve
    - delete
    - update"""
    return reverse("exercise:exerciselog-detail", args=[id])


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


class ExerciseLogCreationTest(TestCase):
    """class for the test operation related to the creation process"""

    def setUp(self):
        self.user = create_user()
        self.tmp_user = create_user(email='tmp@gmail.com')
        self.client = APIClient()
        self.workout_log = create_workout_log(
            user=self.user, name='defaultWorkoutLog')
        self.exercise = create_exercise(name='defaultExercise',
                                        user=self.user)
        self.client.force_authenticate(self.user)

    def test_create_exercise_log_with_nonauth_user_error(self):
        """
        Test ERROR: creating an exercise log with an unauthinticated user"""
        tmp_client = APIClient()
        payload = {
            'workout_log': self.workout_log.id,
            'exercise_name': self.exercise.name
        }
        res = tmp_client.post(EXERCISE_LOG_LIST_CREATE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_exercise_log_suc(self):
        """
        Test creating an exercise log"""
        payload = {
            'workout_log': self.workout_log.id,
            'exercise_name': self.exercise.name
        }
        res = self.client.post(EXERCISE_LOG_LIST_CREATE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data['user'], self.user.id)
        self.assertEqual(res.data['workout_log'], self.workout_log.id)
        self.assertEqual(res.data['exercise']['id'], self.exercise.id)
        self.assertEqual(res.data['exercise']['name'], self.exercise.name)
        self.assertFalse(res.data['notes'])
        self.assertFalse(res.data['number_of_sets'])
        self.assertFalse(res.data['number_of_reps'])
        self.assertFalse(res.data['rest_between_sets_seconds'])
        self.assertFalse(res.data['duration_in_minutes'])

    def test_create_exercise_log_all_fields_suc(self):
        """
        Test SUCCESS: create an exercise log with all field"""
        payload = {
            'exercise_name': self.exercise.name,
            'workout_log': self.workout_log.id,
            'notes': 'note',
            'number_of_sets': 5,
            'number_of_reps': 2,
            'rest_between_sets_seconds': 20,
            'duration_in_minutes': 3,
            'rest_is_in_minutes': False
        }
        res = self.client.post(EXERCISE_LOG_LIST_CREATE_URL, payload)
        for key in payload.keys():
            if key == 'exercise_name' or key == 'rest_is_in_minutes':
                continue
            self.assertEqual(res.data[key], payload[key])

    def test_create_exercise_log_rest_in_minutes_convert_suc(self):
        """
        Test SUCCESS: create an exercise log with rest time in minutes"""
        payload = {
            'exercise_name': self.exercise.name,
            'workout_log': self.workout_log.id,
            'number_of_sets': 52,
            'rest_between_sets_seconds': 2,
            'rest_is_in_minutes': True
        }
        res = self.client.post(EXERCISE_LOG_LIST_CREATE_URL, payload)
        self.assertEqual(res.data['rest_between_sets_seconds'], 120)

    def test_create_exercise_log_with_diff_case_for_name_suc(self):
        """
        Test SUCCESS: create an exercise log with
        changing the case for the name"""
        payload = {
            'workout_log': self.workout_log.id,
            'exercise_name': self.exercise.name.upper()
        }
        res = self.client.post(EXERCISE_LOG_LIST_CREATE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data['user'], self.user.id)
        self.assertEqual(res.data['workout_log'], self.workout_log.id)
        self.assertEqual(res.data['exercise']['id'], self.exercise.id)
        self.assertEqual(res.data['exercise']['name'], self.exercise.name)

    def test_create_exercise_log_with_spaces_for_name_suc(self):
        """
        Test SUCCESS: create an exercise log with
        changing the spaces before the name"""
        payload = {
            'workout_log': self.workout_log.id,
            'exercise_name': "    "+self.exercise.name+"    "
        }
        res = self.client.post(EXERCISE_LOG_LIST_CREATE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data['user'], self.user.id)
        self.assertEqual(res.data['workout_log'], self.workout_log.id)
        self.assertEqual(res.data['exercise']['id'], self.exercise.id)
        self.assertEqual(res.data['exercise']['name'], self.exercise.name)

    def test_create_exercise_log_with_new_name_suc(self):
        """
        Test SUCCESS: creating an exercise log aith an exercise
        name that does not exist in the Exercise Table, it will create it
        """
        payload = {
            'workout_log': self.workout_log.id,
            'exercise_name': 'new exercise'
        }
        res = self.client.post(EXERCISE_LOG_LIST_CREATE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data['user'], self.user.id)
        self.assertEqual(res.data['workout_log'], self.workout_log.id)
        new_exercise = Exercise.objects.get_CI(name='new exercise',
                                               user=self.user)
        self.assertEqual(res.data['exercise']['id'], new_exercise.id)
        self.assertEqual(res.data['exercise']['name'], new_exercise.name)
        self.assertFalse(new_exercise.description)
        self.assertEqual(new_exercise.user, self.user)

    def test_create_exercise_log_with_valid_name_cases_suc(self):
        """
        Test SUCCESS: creating an exercise log aith an exercise
        name that does not exist in the Exercise Table, but all valid values
        """
        valid_names = ["Z1()", "z-1", " z - 1 ", " z' - 1 '"]
        for valid_name in valid_names:
            payload = {
                'workout_log': self.workout_log.id,
                'exercise_name': f'{valid_name}'
                }
            res = self.client.post(EXERCISE_LOG_LIST_CREATE_URL, payload)
            self.assertEqual(res.status_code, status.HTTP_201_CREATED)
            self.assertEqual(res.data['user'], self.user.id)
            self.assertEqual(res.data['workout_log'], self.workout_log.id)
            new_exercise = Exercise.objects.get_CI(
                name=payload['exercise_name'].strip(), user=self.user)
            self.assertEqual(res.data['exercise']['id'], new_exercise.id)
            self.assertEqual(res.data['exercise']['name'], new_exercise.name)
            self.assertFalse(new_exercise.description)
            self.assertEqual(new_exercise.user, self.user)

    def test_create_exercise_log_exercise_name_start_no_char_error(self):
        """
        Test ERROR: create an exercise log with a new exercise name
        with name that does note start with a character
        """
        invalid_names = ['1f', "-Z", "'Z", "(Z)"]
        for invalid_name in invalid_names:
            payload = {
                'workout_log': self.workout_log.id,
                'exercise_name': f'{invalid_name}'
                }
            res = self.client.post(EXERCISE_LOG_LIST_CREATE_URL, payload)
            self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn('Name must start with a letter.',
                          res.data['exercise_name'])

    def test_create_exercise_log_exercise_name_invalid_error(self):
        """
        Test ERROR: create an exercise log with a new invalid exercise name
        """
        invalid_names = ['A!', "Z @", "z %", "Z=", "c#", "c++", "d$", "s{}",
                         "S[]", "X `", "d \"", "q ~", "ahmed ?", "awab >",
                         "a ,", "d <"]
        for invalid_name in invalid_names:
            payload = {
                'workout_log': self.workout_log.id,
                'exercise_name': f'{invalid_name}'
                }
            res = self.client.post(EXERCISE_LOG_LIST_CREATE_URL, payload)
            self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn('Name can only contain: (letters, numbers, spaces, hyphens, parentheses, and apostrophes)', res.data['exercise_name']) # noqa

    def test_create_exercise_log_exercise_name_consicutive_spaces_error(self):
        """
        Test ERROR: create an exercise log with a new invalid exercise name
        that has consicutive spaces in it
        """
        invalid_names = ['A  a', "Z x c     f", "z c   d f"]
        for valid_name in invalid_names:
            payload = {
                'workout_log': self.workout_log.id,
                'exercise_name': f'{valid_name}'
                }
            res = self.client.post(EXERCISE_LOG_LIST_CREATE_URL, payload)
            self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn('Name cannot contain consecutive spaces.',
                          res.data['exercise_name'])

    def test_create_exercise_log_no_exercise_name_workout_error(self):
        """
        Test ERROR: creating an exercise log without workout or
        an exercise name will cause an error"""
        payload = {
            'workout_log': self.workout_log.id
        }
        res = self.client.post(EXERCISE_LOG_LIST_CREATE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        payload = {
            'exercise_name': self.exercise.name
        }
        res = self.client.post(EXERCISE_LOG_LIST_CREATE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_exercise_log_empty_exercise_name_error(self):
        """
        Test ERROR: creating an exercise log with an empty name"""
        payload = {
            'workout_log': self.workout_log.id,
            'exercise_name': ''
        }
        res = self.client.post(EXERCISE_LOG_LIST_CREATE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_exercise_log_diff_user_error(self):
        """
        Test ERROR: creating an exercise log with a diifenrent
        user than is the one logged"""
        payload = {
            'workout_log': self.workout_log.id,
            'exercise_name': self.exercise.name,
            'user': self.tmp_user.id
        }
        res = self.client.post(EXERCISE_LOG_LIST_CREATE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data['user'], self.user.id)

    def test_create_exercise_log_with_other_user_exercise_name_error(self):
        """
        Test ERROR: creating an exercise that has the name of
        an exercise belonging to other user
        -note: it will create a new exercise object
        """
        new_exercise_diff_user = create_exercise(name='other user exercise',
                                                 user=self.tmp_user)
        exer = Exercise.objects.get_CI(name=new_exercise_diff_user.name,
                                       user=self.tmp_user)
        self.assertTrue(exer)  # make sure that the new exercise exists
        payload = {
            'exercise_name': new_exercise_diff_user.name,
            'workout_log': self.workout_log.id
        }
        res = self.client.post(EXERCISE_LOG_LIST_CREATE_URL, payload)
        # a new record with the same name but different user is created
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data['user'], self.user.id)
        self.assertEqual(res.data['workout_log'], self.workout_log.id)
        # get the new record info
        new_exercise_same_user = \
            Exercise.objects.get_CI(name=new_exercise_diff_user.name,
                                    user=self.user)
        self.assertEqual(res.data['exercise']['id'],
                         new_exercise_same_user.id)
        self.assertNotEqual(res.data['exercise']['id'],
                            new_exercise_diff_user.id)

    def test_create_exercise_log_with_other_user_workout_log_error(self):
        """
        Test ERROR: creating an exercise log that has a workout log of
        another user"""
        new_workout_log = create_workout_log(user=self.tmp_user)
        workout = WorkoutLog.objects.get(id=new_workout_log.id)
        self.assertTrue(workout)  # make sure that the new workout exists
        payload = {
            'exercise_name': self.exercise,
            'workout_log': new_workout_log.id
        }
        res = self.client.post(EXERCISE_LOG_LIST_CREATE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_exercise_log_sets_rest_edge_case_error(self):
        """
        Test ERROR: creating an exercise log with one or less sets
        and a rest time between sets
        - note: there should not be rest between sets if it is one or less"""
        payload = {
            'exercise_name': self.exercise.name,
            'workout_log': self.workout_log.id,
            'number_of_sets': 1,
            'rest_between_sets_seconds': 20
        }
        msg = "you can not have rest time without sets. at least two sets"
        res = self.client.post(EXERCISE_LOG_LIST_CREATE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(msg, res.data)

    def test_create_exercise_log_sets_reps_edge_case_error(self):
        """
        Test ERROR: creating an exercise log with zero sets
        and a number of reps
        - note: there should not be reps if sets is less than 1"""
        payload = {
            'exercise_name': self.exercise.name,
            'workout_log': self.workout_log.id,
            'number_of_sets': 0,
            'number_of_reps': 50
        }
        msg = "you can not have reps without a set. at least one set"
        res = self.client.post(EXERCISE_LOG_LIST_CREATE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(msg, res.data)

    def test_create_exercise_log_sets_reps_rest_negative_error(self):
        """
        Test ERROR: trying create an exercise log with negative value
        for sets, reps, duration or rest time"""
        payload = {
            'exercise_name': self.exercise.name,
            'workout_log': self.workout_log.id,
            'number_of_sets': -2
        }
        res = self.client.post(EXERCISE_LOG_LIST_CREATE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        payload.pop('number_of_sets')
        payload['number_of_reps'] = -2
        res = self.client.post(EXERCISE_LOG_LIST_CREATE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        payload.pop('number_of_reps')
        payload['rest_between_sets_seconds'] = -2
        res = self.client.post(EXERCISE_LOG_LIST_CREATE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        payload['rest_is_in_minutes'] = True
        res = self.client.post(EXERCISE_LOG_LIST_CREATE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        payload.pop('rest_is_in_minutes')
        payload['duration_in_minutes'] = -2
        res = self.client.post(EXERCISE_LOG_LIST_CREATE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)


class ExerciseLogRetrieveListTest(TestCase):
    """class for the test operation related to
    the retrieving and listing  process"""

    def setUp(self):
        self.user = create_user()
        self.tmp_user = create_user(email='tmp@gmail.com')
        self.client = APIClient()
        self.workout_log = create_workout_log(
            user=self.user, name='defaultWorkoutLog')
        self.exercise = create_exercise(name='defaultExercise',
                                        user=self.user)
        self.exercise_log = ExerciseLog.objects.create(
            user=self.user, workout_log=self.workout_log,
            exercise=self.exercise, notes='defaultExerciseLogNote')
        self.client.force_authenticate(self.user)

    def test_retrieve_exercise_log_with_nonauth_user_error(self):
        """
        Test ERROR: creating an exercise log with an unauthinticated user"""
        tmp_client = APIClient()
        res = tmp_client.get(EXERCISE_LOG_LIST_CREATE_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        res = tmp_client.get(GET_EXERCISE_LOG_DETAIL_URL(
            self.exercise_log.id))
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_exercise_logs_with_nonauth_user_error(self):
        """
        Test ERROR: list exercise logs with an unauthinticated user"""
        tmp_client = APIClient()
        res = tmp_client.get(EXERCISE_LOG_LIST_CREATE_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_exercise_log_suc(self):
        """
        Test SUCCESS: retrieving a specific exercise log"""
        URL = GET_EXERCISE_LOG_DETAIL_URL(self.exercise_log.id)
        res = self.client.get(URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['exercise']['id'], self.exercise.id)
        self.assertEqual(res.data['exercise']['name'], self.exercise.name)
        self.assertEqual(res.data['user'], self.user.id)
        self.assertEqual(res.data['workout_log'], self.workout_log.id)
        self.assertEqual(res.data['notes'], 'defaultExerciseLogNote')
        self.assertFalse(res.data['number_of_sets'])
        self.assertFalse(res.data['number_of_reps'])
        self.assertFalse(res.data['rest_between_sets_seconds'])
        self.assertFalse(res.data['duration_in_minutes'])

    def test_retrieve_other_user_exercise_log_error(self):
        """
        Test ERROR: retrieving another user's exercise log
        - note: it will be treated as it does not exists because we
        handle this when specifying the get_queryset"""
        other_exercise_log = ExerciseLog.objects.create(
            exercise=self.exercise, workout_log=self.workout_log,
            user=self.tmp_user)
        URL = GET_EXERCISE_LOG_DETAIL_URL(other_exercise_log.id)
        res = self.client.get(URL)
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_list_exercise_logs_suc(self):
        """
        Test SUCCESS: listing all user exercises, and make sure that
        it only returns user exercie logs"""
        exer_log1 = create_exercise_log(user=self.user,
                                        exercise=self.exercise,
                                        workout=self.workout_log,
                                        notes='note1')
        exer_log2 = create_exercise_log(user=self.user,
                                        exercise=self.exercise,
                                        workout=self.workout_log,
                                        notes='note2')
        exer_log3 = create_exercise_log(user=self.tmp_user,
                                        exercise=self.exercise,
                                        workout=self.workout_log,
                                        notes='note3')
        res = self.client.get(EXERCISE_LOG_LIST_CREATE_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        exer_log_ids = [exer_log['id'] for exer_log in res.data]
        exer_log_notes = [exer_log['notes'] for exer_log in res.data]
        self.assertIn(exer_log1.id, exer_log_ids)
        self.assertIn(exer_log2.id, exer_log_ids)
        self.assertIn(exer_log1.notes, exer_log_notes)
        self.assertIn(exer_log2.notes, exer_log_notes)
        self.assertNotIn(exer_log3.id, exer_log_ids)
        self.assertNotIn(exer_log3.notes, exer_log_notes)


class ExerciseLogUpdateTest(TestCase):
    """class for the test operation related to the update process"""

    def setUp(self):
        self.user = create_user()
        self.tmp_user = create_user(email='tmp@gmail.com')
        self.client = APIClient()
        self.workout_log = create_workout_log(
            user=self.user, name='defaultWorkoutLog')
        self.exercise = create_exercise(name='defaultExercise',
                                        user=self.user)
        self.exercise_log = ExerciseLog.objects.create(
            user=self.user, workout_log=self.workout_log,
            exercise=self.exercise, notes='defaultExerciseLogNote')
        self.client.force_authenticate(self.user)
        payload = {
            'notes': 'new note',
            'number_of_sets': 5,
            'number_of_reps': 2,
            'rest_between_sets_seconds': 20,
            'duration_in_minutes': 3
        }
        self.full_exercise_log = create_exercise_log(exercise=self.exercise,
                                                     workout=self.workout_log,
                                                     user=self.user, **payload)

    def test_update_with_nonauth_user_error(self):
        """
        Test ERROR: updating an exercise
        log with an unauthinticated user
        """
        tmp_client = APIClient()
        payload = {
            'notes': 'new notes'
        }
        res = tmp_client.patch(
            GET_EXERCISE_LOG_DETAIL_URL(self.exercise_log.id), payload)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_partial_update_exercise_log_suc(self):
        """
        Test SUCCESS: partial update on an exercise log
        """
        payload = {
            'notes': 'new note',
            'number_of_sets': 10,
            'number_of_reps': 200,
            'rest_between_sets_seconds': 2,
            'duration_in_minutes': 3,
        }
        URL = GET_EXERCISE_LOG_DETAIL_URL(self.exercise_log.id)
        res = self.client.patch(URL, payload)
        self.exercise_log.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        for key in payload.keys():
            self.assertEqual(res.data[key], payload[key])

    def test_partial_update_in_minutes_exercise_log_suc(self):
        """
        Test SUCCESS: partial update on an exercise log for
        the minutes to second flag for rest between stes
        """
        self.exercise_log.number_of_sets = 2
        self.exercise_log.rest_between_sets_seconds = 2
        self.exercise_log.save()
        payload = {
            'rest_is_in_minutes': True
        }
        URL = GET_EXERCISE_LOG_DETAIL_URL(self.exercise_log.id)
        res = self.client.patch(URL, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['rest_between_sets_seconds'], 120)

    def test_partial_update_exercise_log_with_exist_exercise_name_suc(self):
        """
        Test SUCCESS: partial update on an exercise log for
        the exercise name to an already existing exercise
        """
        new_exer = create_exercise(user=self.user, name='new name')
        payload = {
            'exercise_name': new_exer.name
        }
        URL = GET_EXERCISE_LOG_DETAIL_URL(self.exercise_log.id)
        res = self.client.patch(URL, payload)
        self.exercise_log.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['exercise']['id'], new_exer.id)
        self.assertEqual(res.data['exercise']['name'], new_exer.name)
        self.assertEqual(self.exercise_log.exercise.id, new_exer.id)
        self.assertEqual(self.exercise_log.exercise.name, new_exer.name)

    def test_partial_update_exercise_log_with_new_exercise_name_suc(self):
        """
        Test SUCCESS: partial update on an exercise log for
        the exercise name to a new exercise
        """
        payload = {
            'exercise_name': 'new exercise name'
        }
        URL = GET_EXERCISE_LOG_DETAIL_URL(self.exercise_log.id)
        res = self.client.patch(URL, payload)
        self.exercise_log.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        new_exer = Exercise.objects.get_CI(name='new exercise name',
                                           user=self.user)
        self.assertTrue(new_exer)  # make sure new exercise has been created
        self.assertEqual(res.data['exercise']['id'], new_exer.id)
        self.assertEqual(res.data['exercise']['name'], new_exer.name)
        self.assertEqual(self.exercise_log.exercise.id, new_exer.id)
        self.assertEqual(self.exercise_log.exercise.name, new_exer.name)

    def test_partial_update_exercise_log_new_name_valid_cases_suc(self):
        """
        Test SUCCESS: updating an exercise log with a valid name
        """
        URL = GET_EXERCISE_LOG_DETAIL_URL(self.exercise_log.id)
        self.exercise_log.notes = 'old notes'
        self.exercise_log.save()
        valid_names = ["Z1()", "z-1", " z - 1 ", " z' - 1 '"]
        for valid_name in valid_names:
            res = self.client.patch(URL, {'exercise_name': f"{valid_name}"})
            self.exercise_log.refresh_from_db()
            self.assertEqual(res.status_code, status.HTTP_200_OK)
            self.assertEqual(self.exercise_log.exercise.name,
                             valid_name.strip())
            self.assertEqual(self.exercise_log.notes, 'old notes')

    def test_full_update_exercise_log_suc(self):
        """
        Test SUCCESS: full update on an existing exercise log
        - note: according to my implementation i ignore work_out_log in update
        """
        payload = {
            'exercise_name': 'new name exercise',
            'workout_log': self.workout_log.id,
            'notes': 'new note',
            'number_of_sets': 5,
            'number_of_reps': 2,
            'rest_between_sets_seconds': 20,
            'duration_in_minutes': 3,
            'rest_is_in_minutes': False
        }
        URL = GET_EXERCISE_LOG_DETAIL_URL(self.exercise_log.id)
        self.client.put(URL, payload)
        self.exercise_log.refresh_from_db()
        for key in payload.keys():
            if key in ['exercise_name', 'rest_is_in_minutes', 'workout_log']:
                continue
            self.assertEqual(self.exercise_log.__getattribute__(key),
                             payload[key])
        new_exer = Exercise.objects.get_CI(name='new name exercise',
                                           user=self.user)
        self.assertEqual(self.exercise_log.exercise.id, new_exer.id)
        self.assertEqual(self.exercise_log.exercise.name, new_exer.name)

    def test_partial_update_exercise_log_new_name_invalid_cases_error(self):
        """
        Test ERROR: updating an exercise log with an invalid name
        """
        URL = GET_EXERCISE_LOG_DETAIL_URL(self.exercise_log.id)
        invalid_names = ['A!', "Z @", "z %", "Z=", "c#", "c++", "d$", "s{}",
                         "S[]", "X `", "d \"", "q ~", "ahmed ?", "awab >",
                         "a ,", "d <", '1f', "-Z", "'Z", "(Z)",
                         'A  a', "Z x c     f", "z c   d f"]
        for invalid_name in invalid_names:
            res = self.client.patch(URL, {'exercise_name': f"{invalid_name}"})
            self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertNotEqual(self.exercise_log.exercise.name,
                                invalid_name.strip())

    def test_update_exercise_log_no_name_error(self):
        """
        Test ERROR: full updaing an exercise log without name
        """
        payload = {
            'workout_log': self.workout_log.id,
            'notes': 'new note',
            'number_of_sets': 5,
            'number_of_reps': 2,
            'rest_between_sets_seconds': 20,
            'duration_in_minutes': 3,
            'rest_is_in_minutes': False
        }
        URL = GET_EXERCISE_LOG_DETAIL_URL(self.exercise_log.id)
        res = self.client.put(URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.exercise_log.refresh_from_db()
        for key in payload.keys():
            if key in ['exercise_name', 'rest_is_in_minutes', 'workout_log']:
                continue
            self.assertNotEqual(self.exercise_log.__getattribute__(key),
                                payload[key])
        with self.assertRaises(Exercise.DoesNotExist):
            Exercise.objects.get_CI(name='new name exercise', user=self.user)

    def test_update_exercise_log_empty_name_error(self):
        """
        Test ERROR: full updaing an exercise log without name
        """
        payload = {
            'exercise_name': '',
            'workout_log': self.workout_log.id,
            'notes': 'new note',
            'number_of_sets': 5,
            'number_of_reps': 2,
            'rest_between_sets_seconds': 20,
            'duration_in_minutes': 3,
            'rest_is_in_minutes': False
        }
        URL = GET_EXERCISE_LOG_DETAIL_URL(self.exercise_log.id)
        res = self.client.put(URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.exercise_log.refresh_from_db()
        for key in payload.keys():
            if key in ['exercise_name', 'rest_is_in_minutes', 'workout_log']:
                continue
            self.assertNotEqual(self.exercise_log.__getattribute__(key),
                                payload[key])
        with self.assertRaises(Exercise.DoesNotExist):
            Exercise.objects.get_CI(name=payload['exercise_name'],
                                    user=self.user)

    def test_update_exercise_log_diff_user_error(self):
        """
        Test ERROR: try update the user
        - note: it will just ignore it
        """
        payload = {
            'user': self.tmp_user.id
        }
        URL = GET_EXERCISE_LOG_DETAIL_URL(self.exercise_log.id)
        res = self.client.patch(URL, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(self.exercise_log.user, self.user)

    def test_update_exercise_log_sets_rest_edge_case_error(self):
        """
        Test ERROR: upadting an exercise log with one or less sets
        and a rest time between sets
        - note: there should not be rest between sets if it is one or less
        """
        payload = {
            'number_of_sets': 1
        }
        URL = GET_EXERCISE_LOG_DETAIL_URL(self.full_exercise_log.id)
        res = self.client.patch(URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        msg = "you can not have rest time without sets. at least two sets"
        self.assertIn(msg, res.data)

    def test_update_exercise_log_sets_reps_edge_case_error(self):
        """
        Test ERROR: upadting an exercise log with less than one set
        and provide reps
        - note: there should not be rest between sets if it is one or less
        """
        payload = {
            'number_of_sets': 0,
            'number_of_reps': 1
        }
        URL = GET_EXERCISE_LOG_DETAIL_URL(self.full_exercise_log.id)
        res = self.client.patch(URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        msg = "you can not have reps without a set. at least one set"
        self.assertIn(msg, res.data)

    def test_update_exercise_log_sets_reps_rest_negative_error(self):
        """
        Test ERROR: trying update an exercise log with negative values
        for sets, reps, duration or rest time
        """
        URL = GET_EXERCISE_LOG_DETAIL_URL(self.full_exercise_log.id)
        payload = {'number_of_sets': -2}
        res = self.client.patch(URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        payload = {'number_of_reps': -2}
        res = self.client.patch(URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        payload = {'rest_between_sets_seconds': -2}
        res = self.client.patch(URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        payload = {'duration_in_minutes': -2}
        res = self.client.patch(URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)


class ExerciseLogDeleteTest(TestCase):
    """class for the test operation related to the update process"""

    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.workout_log = create_workout_log(
            user=self.user, name='defaultWorkoutLog')
        self.exercise = create_exercise(name='defaultExercise',
                                        user=self.user)
        self.exercise_log = ExerciseLog.objects.create(
            user=self.user, workout_log=self.workout_log,
            exercise=self.exercise, notes='defaultExerciseLogNote')
        self.client.force_authenticate(self.user)

    def test_deleting_with_nonauth_user_error(self):
        """
        Test ERROR: deleting an exercise log with an unauthenticated user"""
        tmp_client = APIClient()
        res = tmp_client.delete(GET_EXERCISE_LOG_DETAIL_URL(
            self.exercise_log.id))
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_deleting_exercise_suc(self):
        """
        Test SUCCESS: deleting an exercise"""
        URL = GET_EXERCISE_LOG_DETAIL_URL(self.exercise_log.id)
        res = self.client.delete(URL)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
