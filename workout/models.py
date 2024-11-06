from django.db import models
from user.models import User
from django.utils import timezone


def get_default_workout_log_name():
    """A helper function to create the default
    name for a workoutlog"""
    current_time = timezone.localtime(timezone.now())
    day_name = current_time.strftime('%A')
    hour = current_time.strftime('%H')
    return f"{day_name}_{hour}_workout"


class WorkoutLog(models.Model):
    """Workout Logs that consist of the exercises
    and sets of each one and info about each of them, and so on
    - name field: the default value that frontend should gave me
                  is the '`dayname`_workout'
    """
    name = models.CharField(max_length=254)
    description = models.TextField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    duration = models.DurationField(null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        # set the default value for the name if not given
        if not self.name:
            self.name = get_default_workout_log_name()
        # Automatically calculate duration when finished_at is set
        if self.finished_at and self.started_at:
            self.duration = self.finished_at - self.started_at
        super().save(*args, **kwargs)
