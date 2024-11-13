from django.db import models
from django.contrib.auth import get_user_model
from workout.models import WorkoutLog
from .validators import validate_exercise_name
User = get_user_model()


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
    - Exercise class that is responsible of the Exercise
    in each workout log
    - each exercise is unique byt it's name
    """
    name = models.CharField(max_length=254,
                            null=False,
                            blank=False,
                            validators=[validate_exercise_name])
    description = models.TextField(null=True, blank=True)
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
            raise KeyError("name has to be provided")

        # Manually trigger the full validation process
        self.full_clean()  # This will call the field-level validators

        # strip whitespace
        self.name = self.name.strip()

        # Check for duplicates, excluding the current instance
        exercises_same_name = Exercise.objects.filter_CI(
            name=self.name, user=self.user).exclude(pk=self.pk).first()
        if exercises_same_name:
            raise KeyError(
                f"An exercise with the name '{exercises_same_name.name}' already exists.") # noqa

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name + " with " + self.user.__str__()


class ExerciseLog(models.Model):
    workout_log = models.ForeignKey(WorkoutLog, on_delete=models.CASCADE)
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    notes = models.TextField(null=True, blank=True)
    number_of_sets = models.PositiveSmallIntegerField(null=True, blank=True)
    number_of_reps = models.PositiveSmallIntegerField(null=True, blank=True)
    rest_between_sets_seconds = models.PositiveSmallIntegerField(null=True,
                                                                 blank=True)
    duration_in_minutes = models.PositiveIntegerField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.number_of_sets:
            if self.number_of_sets < 2:
                self.rest_between_sets_seconds = 0
            if self.number_of_sets < 1:
                self.number_of_reps = 0
        else:
            self.number_of_reps = None
            self.rest_between_sets_seconds = None
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Exercise {self.exercise.name} in workout\
 {self.workout_log.name}"
