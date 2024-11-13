from rest_framework import serializers
from exercise.models import Exercise, ExerciseLog
from .Exercise_serializers import ExerciseListSerializer
from exercise.validators import validate_exercise_name


class ExerciseLogSerializer(serializers.ModelSerializer):
    """Serializer for the ExerciseLog model endpoints"""
    exercise_name = serializers.CharField(write_only=True, max_length=254,
                                          validators=[validate_exercise_name])
    rest_is_in_minutes = serializers.BooleanField(
        write_only=True, default=False)
    exercise = ExerciseListSerializer(read_only=True)

    class Meta:
        model = ExerciseLog
        fields = ['id', 'exercise_name', 'workout_log', 'user',
                  'exercise', 'notes', 'number_of_sets',
                  'number_of_reps', 'rest_between_sets_seconds',
                  'duration_in_minutes', 'rest_is_in_minutes', 'created_at']
        read_only_fields = ['id', 'exercise', 'user', 'created_at']
        write_only_fields = ['rest_is_in_minutes', 'exercise_name']

    @staticmethod
    def _process_sets_reps_rest(instance, validated_data):
        """
        - - A helper function to handle the edge cases of sets, reps and the
        rest time between sets, and convert rest time to seconds if needed
        - constrains it checks:
            - reps can not have value if sets is <= 0
            - rest can not have value if sets is <= 1
        - parameters
            - instance:
                - None if called at creation
                - have a value if called at update
            - validated_data: fields values that has been sent
        - return value:
            - validated data after final validation
        """
        backup_sets = backup_reps = backup_rest = None
        if instance:
            backup_sets = instance.number_of_sets
            backup_reps = instance.number_of_reps
            backup_rest = instance.rest_between_sets_seconds
        sets = validated_data.get('number_of_sets', backup_sets)
        reps = validated_data.get('number_of_reps', backup_reps)
        rest = validated_data.pop('rest_between_sets_seconds', backup_rest)
        res_is_in_minutes = validated_data.pop('rest_is_in_minutes', None)

        # handling edge cases
        if reps and not sets:
            msg = "you can not have reps without a set. at least one set"
            raise serializers.ValidationError(msg)
        if rest and sets <= 1:
            msg = "you can not have rest time without sets. at least two sets"
            raise serializers.ValidationError(msg)
        if res_is_in_minutes and rest:
            rest = int(rest * 60)

        validated_data['rest_between_sets_seconds'] = rest
        return validated_data

    def validate_exercise_name(self, exercise_name):
        """make sure that exercise_name is not empty or None"""
        if not exercise_name:
            raise serializers.ValidationError("An exercise name is required")
        return exercise_name

    def validate_workout_log(self, workout):
        """make sure that the workout_log belongs to the current user"""
        if not self.instance:
            user = self.context['request'].user
            if workout.user != user:
                workout = None
                raise serializers.ValidationError(
                    "You can only add logs to your own workout logs")
            return workout
        return self.instance.workout_log

    def get_or_create_exercise(self, exercise_name):
        """Make sure that the exercise belongs to the current
        user or create if it doesn't exist"""
        user = self.context['request'].user
        exercise = None
        try:
            exercise = Exercise.objects.get_CI(name=exercise_name, user=user)
        except Exercise.DoesNotExist:
            exercise = Exercise.objects.create(
                name=exercise_name, user=user)
        return exercise

    def validate(self, data):
        """Perform validation in the object level"""
        # validate the exercise field
        exercise_name = data.pop('exercise_name', None)
        if exercise_name:
            exercise = self.get_or_create_exercise(exercise_name)
            if not exercise:
                raise \
                    serializers.ValidationError("System Error: while creating exercise log") # noqa
            data['exercise'] = exercise
        return data

    def create(self, validated_data):
        # process sets, reps, rest time
        validated_data =\
            ExerciseLogSerializer._process_sets_reps_rest(None, validated_data)

        # set the user
        user = self.context['request'].user
        validated_data['user'] = user
        exercise = ExerciseLog.objects.create(**validated_data)
        return exercise

    def update(self, instance, validated_data):
        # handling updating workout ignore
        validated_data.pop('workout_log', None)

        # process sets, reps, rest time
        validated_data = ExerciseLogSerializer\
            ._process_sets_reps_rest(instance, validated_data)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class ExerciseLogProgressListSerializer(serializers.ModelSerializer):
    """
    serializer of the return to the list of progress of a certain exercise
    """
    class Meta:
        model = ExerciseLog
        fields = ['number_of_sets', 'number_of_reps',
                  'rest_between_sets_seconds', 'duration_in_minutes',
                  'created_at', 'workout_log']
