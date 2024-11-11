from rest_framework import serializers
from exercise.models import Exercise


class ExerciseSerializer(serializers.ModelSerializer):
    """Serializer for the Exercise model enpoints"""
    class Meta:
        model = Exercise
        fields = ['id', 'name', 'description', 'user']
        read_only_fields = ['id', 'user']

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
