from django.db import models

from django.utils import timezone
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
User = get_user_model()


def get_default_workout_log_name():
    """A helper function to create the default
    name for a workoutlog"""
    current_time = timezone.localtime(timezone.now())
    day_name = current_time.strftime('%A')
    hour = current_time.strftime('%H')
    return f"{day_name}_{hour}_workout"


class ExerciseManager(models.Manager):
    """Class for managing some exercise constrains:
    - name is case in-sensitive
    - name is stored in the database with the same case not lowored
    - you can Query name in in-sensitive manner
    """
    def get_CI(self, name, **extrakwargs):
        """
        Getting an exercise case-insensitively
        """
        return self.get(name__iexact=name, **extrakwargs)

    def filter_CI(self, name, **extrakwargs):
        """
        Perform a case-insensitive filter on exercises.
        """
        return self.filter(name__iexact=name, **extrakwargs)


class Exercise(models.Model):
    """
    Exercise calss that is responsible of the Exercise
    in each workout log
    each exercise is unique byt it's name
    """
    name = models.CharField(max_length=254, null=False, blank=False)
    description = models.TextField(null=True, blank=True)
    number_of_sets = models.PositiveSmallIntegerField(null=True, blank=True)
    number_of_reps = models.PositiveSmallIntegerField(null=True, blank=True)
    rest_between_sets_seconds = models.PositiveSmallIntegerField(null=True,
                                                                 blank=True)
    duration_in_minutes = models.PositiveSmallIntegerField(null=True,
                                                           blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    objects = ExerciseManager()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'name'],
                                    name="unique_user_exercise_name")
        ]
        indexes = [
            models.Index(fields=['user', 'name']),
        ]

    def save(self, *args, **kwargs):
        if not self.name:
            raise ValueError("name has to be provided")

        exercises_same_name = Exercise.objects.filter(name__iexact=self.name,
                                                      user=self.user)
        if exercises_same_name.exclude(pk=self.pk).exists():
            raise ValidationError(
                f"An exercise with the name'{self.name}' already exists.")

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name + " with " + self.user.__str__()


class WorkoutLog(models.Model):
    """Workout Logs that consist of the exercises
    and sets of each one and info about each of them, and so on
    - name field: the default value that frontend should gave me
                  is the '`dayname`_workout'
    """
    name = models.CharField(max_length=254, null=True, blank=True)
    description = models.TextField(max_length=1000, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    duration = models.DurationField(null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    exercises = models.ManyToManyField(Exercise, blank=True,
                                       related_name="exercises")

    def save(self, *args, **kwargs):
        # set the default value for the name if not given
        if not self.name:
            self.name = get_default_workout_log_name()
        # Automatically calculate duration when finished_at is set
        if self.finished_at and self.started_at:
            self.duration = self.finished_at - self.started_at
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name + " with " + self.user.__str__()
