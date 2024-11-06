"""
Test Model related to the workout app
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from ..models import (
    WorkoutLog,
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

    def test_create_workout_with_name(self):
        """Test creating user with name"""
        payload = {
            'name': 'Leg day',
            'user': self.user
        }
        workout = WorkoutLog.objects.create(**payload)
        self.assertEqual(workout.name, payload['name'])

    def test_create_workout_without_name(self):
        """Test creating user without name"""
        payload = {
            'user': self.user
        }
        workout = WorkoutLog.objects.create(**payload)
        self.assertEqual(workout.name,
                         get_default_workout_log_name())

    def test_update_workout_without_name(self):
        """Test updating an existed workoutlog
        without specifying a name in the update
        payload, to see if the name will stay the same"""
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

    def test_setting_created_at(self):
        """Test mdifying or setting created_at attribute"""
        with self.assertRaises(Exception):
            WorkoutLog.objects.create(
                created_at=timezone.now()
            )

    def test_update_created_at_error(self):
        """Test updating an the created_at attr,
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

    def test_duration_value(self):
        """test the duration value for the workout value"""
        workout = WorkoutLog.objects.create(
            name="leg day",
            started_at=timezone.now(),
            user=self.user
        )
        workout.finished_at = timezone.now()
        workout.save()
        duration = workout.finished_at - workout.started_at
        self.assertEqual(workout.duration, duration)

    def test_foriegn_key_constrains(self):
        """Test if deleting the user will
        removes the workout of the database"""
        workout = WorkoutLog.objects.create(
            name="leg day",
            user=self.user
        )
        self.user.delete()
        with self.assertRaises(WorkoutLog.DoesNotExist):
            WorkoutLog.objects.get(id=workout.id)
