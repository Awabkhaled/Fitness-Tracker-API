from rest_framework import serializers
from . import models
from django.utils import timezone


class WorkoutLogSerializer(serializers.ModelSerializer):
    """Serializer for handling the
     basic CRUD operation for the WorkoutLogs.
     - it does not handle list, list has another serializer"""
    start_workout = serializers.BooleanField(write_only=True, default=False)
    finish_workout = serializers.BooleanField(write_only=True, default=False)

    class Meta:
        model = models.WorkoutLog
        fields = ['id', 'name', 'description', 'created_at',
                  'started_at', 'finished_at', 'duration',
                  'start_workout', 'finish_workout']
        read_only_fields = ['id', 'started_at',
                            'finished_at', 'created_at', 'duration']

    @staticmethod
    def _handle_start_finish_workout(instance, want_to_start, want_to_finish):
        """A helper function that handles the starting and the
        finishing of a workout with several cases of errors
        it handles:
        - Raising Error if:
            - start and finish a workout at the same time
            - start a workout while it is already started
            - finish a workout while it is already finished
            - finish a workout without starting it
        - Set the time for:
            - started_at attribute if the user want to satrt
            - finished_at attribute if the user want to finish
        """
        already_started = bool(instance.started_at)
        already_finished = bool(instance.finished_at)
        msg = ""
        if want_to_start and want_to_finish:
            msg = "You can't start and finish a workout at the same time"
        elif already_started and want_to_start:
            msg = "You can't start a workout twice"
        elif already_finished and want_to_finish:
            msg = "You can't finish a workout twice"
        elif want_to_finish and not already_started:
            msg = "You can't finish a workout without starting it"

        if msg:
            raise serializers.ValidationError(msg)
        if want_to_start:
            instance.started_at = timezone.localtime(timezone.now())
        elif want_to_finish:
            instance.finished_at = timezone.localtime(timezone.now())
        else:
            msg = """something wrong in your
            _start_or_finish_workout_handling function
             because this should Never been printed"""
            raise Exception(msg)

    def create(self, validated_data):
        """Create a workout_log serializer"""
        start_workout = validated_data.pop('start_workout', None)
        finish_workout = validated_data.pop('finish_workout', None)
        if start_workout or finish_workout:
            msg = "start_workout and finish_workout \
can not be set on creating"
            raise serializers.ValidationError(msg)
        request = self.context.get('request')
        user = request.user
        validated_data['user'] = user
        workout_log = models.WorkoutLog.objects.create(**validated_data)
        return workout_log

    def update(self, instance, validated_data):
        """Updating a workout_log serializer"""
        want_to_start = validated_data.pop('start_workout', None)
        want_to_finish = validated_data.pop('finish_workout', None)
        if want_to_start or want_to_finish:
            WorkoutLogSerializer.\
                _handle_start_finish_workout(instance,
                                             want_to_start, want_to_finish)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class WorkoutLogListSerializer(serializers.ModelSerializer):
    """Serializer for listing WorkoutLogs without details."""
    class Meta:
        model = models.WorkoutLog
        fields = ['id', 'name', 'created_at']
        read_only_fields = ['id', 'name', 'created_at']
