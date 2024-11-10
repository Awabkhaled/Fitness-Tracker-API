"""
This file is for testing the model related operations
for the WorkoutLog model
- Classes:
    - WorkoutLogsTest: for the related operations of WorkoutLog model
    - WorkoutLogsExerciseTest: for exercise related test for WorkoutLog model
- naming conventions:
    - test_...._suc: mean that the test is meant to success the operation
    it meant to do
    - test_...._error: mean that the test is meant to fail the operation
    it meant to do
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from ..models import (
    WorkoutLog,
    Exercise,
    get_default_workout_log_name)
from django.utils import timezone


class WorkoutLogsTest(TestCase):
    """Testing the related operations
    of WorkoutLog model"""

    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.\
            create_user(email='test@gmail.com',
                        password='test1234')

    def test_create_workout_with_name_suc(self):
        """Test SUCCESS: creating user with name"""
        payload = {
            'name': 'Leg day',
            'user': self.user
        }
        workout = WorkoutLog.objects.create(**payload)
        self.assertEqual(workout.name, payload['name'])

    def test_create_workout_without_name_suc(self):
        """Test SUCCESS: creating user without name"""
        payload = {
            'user': self.user
        }
        workout = WorkoutLog.objects.create(**payload)
        self.assertEqual(workout.name,
                         get_default_workout_log_name())

    def test_update_workout_without_name_suc(self):
        """Test SUCCESS: updating an existed workoutlog
        without specifying a name in the update
        payload, will not change the same"""
        workout = WorkoutLog.objects.create(
            name="leg day",
            user=self.user
        )
        payload = {
            'description': 'New description'
        }
        WorkoutLog.objects.filter(id=workout.id).\
            update(**payload)
        self.assertNotEqual(workout.name,
                            get_default_workout_log_name())

    def test_setting_created_at_error(self):
        """Test ERROR: mdifying or setting created_at attribute"""
        with self.assertRaises(Exception):
            WorkoutLog.objects.create(
                created_at=timezone.now()
            )

    def test_update_created_at_error(self):
        """Test ERROR: updating an the created_at attr,
        it should not raise an error
        but it won't change anything"""
        workout = WorkoutLog.objects.create(
            name="leg day",
            user=self.user
        )
        updated_time = \
            timezone.make_aware(timezone.datetime(2002, 11, 8))
        payload = {
            'created_at': updated_time
        }
        WorkoutLog.objects.filter(id=workout.id).update(**payload)
        self.assertNotEqual(workout.created_at, updated_time)

    def test_duration_value_suc(self):
        """Test SUCCESS: the duration value for the workout value"""
        workout = WorkoutLog.objects.create(
            name="leg day",
            started_at=timezone.now(),
            user=self.user
        )
        workout.finished_at = timezone.now()
        workout.save()
        duration = workout.finished_at - workout.started_at
        self.assertEqual(workout.duration, duration)

    def test_foriegn_key_constrains_suc(self):
        """Test SUCCESS: if deleting the user will
        removes the workout of the database"""
        workout = WorkoutLog.objects.create(
            name="leg day",
            user=self.user
        )
        self.user.delete()
        with self.assertRaises(WorkoutLog.DoesNotExist):
            WorkoutLog.objects.get(id=workout.id)


class WorkoutLogsExerciseTest(TestCase):
    """for exercise related tests for WorkoutLog model"""

    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(
            email="user@gmail.com",
            password="test1234"
        )

    def test_create_workout_with_exercise_suc(self):
        """Test SUCCESS: creating a workout with an exercise"""
        workout = WorkoutLog.objects.create(user=self.user)
        exer1 = Exercise.objects.create(user=self.user, name='e1')
        exer2 = Exercise.objects.create(user=self.user, name='e2')
        workout.exercises.add(exer1)
        workout.exercises.add(exer2)
        self.assertIn(exer1, workout.exercises.all())
        self.assertIn(exer2, workout.exercises.all())

    def test_deleting_workout_exercise__suc(self):
        """Test SUCCESS: deleting a workout or an exercise
        does not affect either of them"""
        workout = WorkoutLog.objects.create(user=self.user)
        exer1 = Exercise.objects.create(user=self.user, name='e1')
        workout.exercises.add(exer1)
        # deleting a workout
        workout.delete()
        self.assertFalse(exer1.exercises.all())
        # deleting an exercise
        workout = WorkoutLog.objects.create(user=self.user)
        workout.exercises.add(exer1)
        exer1.delete()
        self.assertFalse(workout.exercises.all())
