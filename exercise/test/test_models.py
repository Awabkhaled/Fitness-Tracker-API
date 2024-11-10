"""
This file is for testing the model related operations
for the exercises model
- Classes:
    - ExerciseTest: for the related operations of Exercise model
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
from ..models import Exercise


def create_exercise(name=None, user=None, **kwargs):
    """A helper method to create an execise"""
    return Exercise.objects.create(name=name, user=user, **kwargs)


class ExerciseTest(TestCase):
    """Testing the related operations
    of the Exercise model"""

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
        with self.assertRaises(ValueError):
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
        exer = create_exercise("unique", self.tmp_user)
        exer.delete()
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

    def test_create_exercise_with_all_fields_suc(self):
        """Test SUCCESS: creating an exercise with all fields"""
        exer = create_exercise(name="exer", user=self.user,
                               description="desc1", number_of_sets=3,
                               number_of_reps=4, rest_between_sets_seconds=5,
                               duration_in_minutes=20)
        self.assertEqual(exer.description, "desc1")
        self.assertEqual(exer.number_of_sets, 3)
        self.assertEqual(exer.number_of_reps, 4)
        self.assertEqual(exer.rest_between_sets_seconds, 5)
        self.assertEqual(exer.duration_in_minutes, 20)

    def test_create_exercise_with_all_fields_default_suc(self):
        """Test SUCCESS: all fields are set to default values"""
        exer = create_exercise(name="exer", user=self.user)
        self.assertIsNone(exer.description)
        self.assertIsNone(exer.number_of_sets)
        self.assertIsNone(exer.number_of_reps)
        self.assertIsNone(exer.rest_between_sets_seconds)
        self.assertIsNone(exer.duration_in_minutes)

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
