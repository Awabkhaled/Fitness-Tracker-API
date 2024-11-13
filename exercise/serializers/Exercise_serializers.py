from rest_framework import serializers
from exercise.models import Exercise


class ExerciseSerializer(serializers.ModelSerializer):
    """Serializer for the Exercise model enpoints"""
    class Meta:
        model = Exercise
        fields = ['id', 'name', 'description', 'user']
        read_only_fields = ['id', 'user']

    def validate_name(self, name):
        """Validate that the exercise name is unique for the user"""
        user = self.context['request'].user
        exercise_id = self.instance.id if self.instance else None

        # Check for duplicates, excluding the current instance
        existing_exercise = Exercise.objects.filter_CI(name=name, user=user)\
            .exclude(pk=exercise_id).first()
        if existing_exercise:
            raise serializers.ValidationError(
                f"An exercise with the name '{existing_exercise.name}' already exists.") # noqa

        return name

    def create(self, validated_data):
        user = self.context.get('request').user
        validated_data['user'] = user
        exercise = Exercise.objects.create(**validated_data)
        return exercise

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class ExerciseListSerializer(serializers.ModelSerializer):
    """Serializer for the Exercise model list enpoint"""
    class Meta:
        model = Exercise
        fields = ['id', 'name']
        read_only_fields = ['id']


class ExerciseSearchSerializer(serializers.Serializer):
    name = serializers.CharField(required=False, max_length=254)
