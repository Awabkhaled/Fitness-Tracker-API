"""
This file is for testing the model related operations
for the exercises model
- Classes:
    - ExerciseTest: for the related operations of Exercise model
    - ExerciseLogTest: for the related operations of ExerciseLog model
- Helper methods:
    - create_exercise: a helper method to crate an exercise
- naming conventions:
    - test_...._suc: mean that the test is meant to success the operation
    it meant to do
    - test_...._error: mean that the test is meant to fail the operation
    it meant to do
"""
from django.contrib.auth import get_user_model
from django.test import TestCase
from exercise.models import Exercise, ExerciseLog
from workout.models import WorkoutLog


def create_exercise(name=None, user=None, **kwargs):
    """A helper method to create an execise"""
    return Exercise.objects.create(name=name, user=user, **kwargs)


class ExerciseTest(TestCase):
    """Testing the related operations of the Exercise model"""

    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create(
                email="test@gmail.com",
                password="test1234"
        )
        cls.tmp_user = get_user_model().objects.create(
                email="tmp@gmail.com",
                password="test1234"
        )
        cls.exercise1 = create_exercise("exer1", cls.user)
        cls.exercise2 = create_exercise("exer2", cls.user)

    def test_create_exercise_suc(self):
        """Test SUCCESS: creating an instance"""
        create_exercise("exer", self.user)
        exer = Exercise.objects.get(name="exer", user=self.user)
        self.assertTrue(exer)
        self.assertEqual(exer.name, "exer")
        self.assertEqual(exer.user, self.user)

    def test_create_exercise_no_user_error(self):
        """Test ERROR: creating an instance
        without user"""
        with self.assertRaises(Exception):
            create_exercise(name="exer1")

    def test_create_exercise_no_name_error(self):
        """Test ERROR: creating an instance
        without name"""
        with self.assertRaises(Exception):
            create_exercise(user=self.user)

    def test_create_exercise_empty_name_error(self):
        """Test ERROR: creating an instance
        with an empty string name"""
        with self.assertRaises(KeyError):
            create_exercise(name='', user=self.user)

    def test_create_exercise_same_name_user_error(self):
        """Test ERROR: creating two instances
        with the same name and the same user"""
        with self.assertRaises(Exception):
            create_exercise(self.exercise1.name, self.user)

    def test_create_exercise_name_case_insensitive_suc(self):
        """Test SUCCESS: all case sensitive creating testing"""
        with self.assertRaises(Exception):
            create_exercise("Exer1", self.user)
        exer = Exercise.objects.get_CI(name="eXeR1", user=self.user)
        self.assertTrue(exer)
        self.assertEqual(exer.user, self.user)

    def test_update_exercise_name_case_insensitive_suc(self):
        """Test SUCCESS: all case sensitive updating testing"""
        with self.assertRaises(Exception):
            exer = Exercise.objects.get_CI(name="Exer2", user=self.user)
            exer.name = "eXeR1"
            exer.save()
        exer = Exercise.objects.get_CI(name="Exer2", user=self.user)
        self.assertEqual(exer.name, "exer2")

    def test_create_exercise_same_name_diff_user_suc(self):
        """Test SUCCESS: creating two instances
        with the same name but not the same user"""
        create_exercise(self.exercise1.name, self.tmp_user)
        exers = Exercise.objects.filter_CI(name=self.exercise1.name)
        self.assertEqual(len(exers), 2)
        self.assertNotEqual(exers[0].user, exers[1].user)

    def test_user_relation_constrains_suc(self):
        """
        Test SUCCESS: delete a user after creating exercise
        with it, should be delete the exercise
        """
        create_exercise("unique", self.tmp_user)
        self.tmp_user.delete()
        with self.assertRaises(Exercise.DoesNotExist):
            Exercise.objects.get_CI(name="unique")

    def test_update_exercise_same_name_user_error(self):
        """Test ERROR: updating an instance to be
         the same name of another exercise with the
         same user"""
        with self.assertRaises(Exception):
            Exercise.objects.filter_CI(
                name=self.exercise2.name, user=self.user)\
                    .update(name=self.exercise1.name)

    def test_update_exercise_suc(self):
        """Test SUCCESS: updating an instance"""
        exer1 = create_exercise("willBeUpdated", self.user)
        Exercise.objects.filter_CI(name=exer1.name, user=self.user)\
            .update(name="new name")
        exer = Exercise.objects.get_CI(name="new name")
        self.assertTrue(exer)

    def test_exercise_manager_suc(self):
        """
        Test SUCCESS: all exercise manager feature
        """
        create_exercise(name="e1", user=self.user, description="desc1")
        create_exercise(name="e1", user=self.tmp_user)
        create_exercise(name='e2', user=self.user)
        create_exercise(name='e2', user=self.tmp_user)
        exer = Exercise.objects.get_CI(name="e1", description="desc1")
        self.assertEqual(exer.user, self.user)
        exer = Exercise.objects.filter_CI(name="e2")
        self.assertEqual(len(exer), 2)
        exer = Exercise.objects.filter_CI(name="E1")
        self.assertEqual(len(exer), 2)

    def test_updating_exercise_suc(self):
        """Test SUCCESS: test updating exercise"""
        self.exercise1.description = "new description"
        self.exercise1.save()
        self.assertEqual(self.exercise1.description, "new description")
        old_name = self.exercise1.name
        self.exercise1.name = "new name"
        self.exercise1.save()
        self.assertEqual(self.exercise1.name, "new name")
        self.exercise1.name = old_name
        self.exercise1.save()

    def test_updating_exercise_existing_name_error(self):
        """Test ERROR: updating an exercise with a name that already exists"""
        tmp_exer = create_exercise(name='tmpExercise', user=self.user)
        self.exercise1.name = 'TmPExeRcise'
        with self.assertRaises(KeyError):
            self.exercise1.save()
        self.exercise1.refresh_from_db()
        self.assertEqual(self.exercise1.name, 'exer1')
        exers = Exercise.objects.filter(user=self.user)
        exers_name = [exer.name for exer in exers]
        self.assertIn('tmpExercise', exers_name)
        self.assertIn('exer1', exers_name)
        self.assertNotIn('TmPExeRcise', exers_name)
        tmp_exer.delete()


class ExerciseLogTest(TestCase):
    """Testing the related operations of the ExerciseLog model"""

    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create(
                email="test@gmail.com",
                password="test1234"
        )
        cls.workout = WorkoutLog.objects.create(
            name='default workoutlog',
            user=cls.user
        )
        cls.exercise = create_exercise("exer1", cls.user)

    def test_create_exerciseLog_suc(self):
        """
        Test SUCCESS: testing creating an exercise log
        """
        ExerciseLog.objects.create(workout_log=self.workout,
                                   exercise=self.exercise, number_of_sets=5,
                                   user=self.user)
        exlog = ExerciseLog.objects.get(workout_log=self.workout,
                                        exercise=self.exercise)
        self.assertEqual(exlog.number_of_sets, 5)
        self.assertEqual(exlog.workout_log, self.workout)
        self.assertEqual(exlog.exercise, self.exercise)
        self.assertEqual(exlog.user, self.user)

    def test_create_exerciseLog_with_all_fields_suc(self):
        """Test SUCCESS: creating an exercise_log with all fields"""
        exlog = ExerciseLog.objects.create(workout_log=self.workout,
                                           exercise=self.exercise,
                                           notes='this is note',
                                           number_of_sets=3, number_of_reps=4,
                                           rest_between_sets_seconds=5,
                                           duration_in_minutes=20,
                                           user=self.user)
        exlog = ExerciseLog.objects.get(id=exlog.id)
        self.assertEqual(exlog.workout_log, self.workout)
        self.assertEqual(exlog.exercise, self.exercise)
        self.assertEqual(exlog.number_of_sets, 3)
        self.assertEqual(exlog.number_of_reps, 4)
        self.assertEqual(exlog.rest_between_sets_seconds, 5)
        self.assertEqual(exlog.duration_in_minutes, 20)
        self.assertEqual(exlog.user, self.user)

    def test_create_exercise_with_all_fields_default_suc(self):
        """Test SUCCESS: all fields are set to default values"""
        exlog = ExerciseLog.objects.create(workout_log=self.workout,
                                           exercise=self.exercise,
                                           user=self.user)
        exlog = ExerciseLog.objects.get(id=exlog.id)
        self.assertIsNone(exlog.notes)
        self.assertIsNone(exlog.number_of_sets)
        self.assertIsNone(exlog.number_of_reps)
        self.assertIsNone(exlog.rest_between_sets_seconds)
        self.assertIsNone(exlog.duration_in_minutes)

    def test_create_exerciseLog_with_no_workout_exercise_or_user_error(self):
        """Test ERROR: creating an exercise log without
        a workout_log or a user"""
        with self.assertRaises(Exception):
            ExerciseLog.objects.create(exercise=self.exercise, user=self.user)
        with self.assertRaises(Exception):
            ExerciseLog.objects.create(workout_log=self.workout,
                                       user=self.user)
        with self.assertRaises(Exception):
            ExerciseLog.objects.create(workout_log=self.workout,
                                       exercise=self.exercise)

    def test_relations_constrains_workout_suc(self):
        """
        Test SUCCESS: delete a workout after creating exercise log
        with it, should be delete the exercise log
        """
        tmp_workout = WorkoutLog.objects.create(user=self.user)
        tmp_exercise = create_exercise("tmpexerise", self.user)
        tmp_user = get_user_model().objects.create(email='tmp@gmail.com',
                                                   password='pass1234')
        ExerciseLog.objects.create(workout_log=tmp_workout, user=tmp_user,
                                   exercise=tmp_exercise, notes='unique')
        tmp_workout.delete()
        with self.assertRaises(ExerciseLog.DoesNotExist):
            ExerciseLog.objects.get(notes='unique')
        tmp_user.delete()
        tmp_exercise.delete()

    def test_relations_constrains_exercise_suc(self):
        """
        Test SUCCESS: delete an exercise after creating exercise log
        with it, should be delete the exercise log
        """
        tmp_workout = WorkoutLog.objects.create(user=self.user)
        tmp_exercise = create_exercise("tmpexerise", self.user)
        tmp_user = get_user_model().objects.create(email='tmp@gmail.com',
                                                   password='pass1234')
        ExerciseLog.objects.create(workout_log=tmp_workout, user=tmp_user,
                                   exercise=tmp_exercise, notes='unique')
        tmp_exercise.delete()
        with self.assertRaises(ExerciseLog.DoesNotExist):
            ExerciseLog.objects.get(notes='unique')
        tmp_user.delete()
        tmp_workout.delete()

    def test_relations_constrains_user_suc(self):
        """
        Test SUCCESS: delete a user after creating exercise log
        with it, should be delete the exercise log
        """
        tmp_workout = WorkoutLog.objects.create(user=self.user)
        tmp_exercise = create_exercise("tmpexerise", self.user)
        tmp_user = get_user_model().objects.create(email='tmp@gmail.com',
                                                   password='pass1234')
        ExerciseLog.objects.create(workout_log=tmp_workout, user=tmp_user,
                                   exercise=tmp_exercise, notes='unique')
        tmp_user.delete()
        with self.assertRaises(ExerciseLog.DoesNotExist):
            ExerciseLog.objects.get(notes='unique')
        tmp_exercise.delete()
        tmp_workout.delete()

    def test_reps_rest_set_to_zero_suc(self):
        """Test SUCCESS: resps is set to 0 if sets is set to 0
        and rest time is set to 0 if sets is set to 1 or less"""
        exlog = ExerciseLog.objects.create(workout_log=self.workout,
                                           exercise=self.exercise,
                                           number_of_sets=10,
                                           number_of_reps=3, user=self.user,
                                           rest_between_sets_seconds=20)
        exlog.number_of_sets = 0
        exlog.save()
        self.assertFalse(exlog.number_of_reps)
        self.assertFalse(exlog.rest_between_sets_seconds)
        exlog.number_of_sets = None
        self.assertIsNone(exlog.number_of_reps)
        self.assertIsNone(exlog.rest_between_sets_seconds)
