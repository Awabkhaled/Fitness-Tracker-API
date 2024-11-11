from rest_framework.viewsets import ModelViewSet
from django.contrib.auth import get_user_model # noqa
from exercise.models import Exercise, ExerciseLog # noqa
from exercise.serializers import ( # noqa
    ExerciseLogSerializer,
    ExerciseSerializer,
    ExerciseListSerializer)
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema


@extend_schema(
    methods=['GET'],
    description='Retriving Exercises related to the current loged user'
)
@extend_schema(
    methods=['POST'],
    description='Creating Exercise with the current loged user'
)
@extend_schema(
    methods=['PUT'],
    description='Updating an Exercise by ID, only by its user'
)
@extend_schema(
    methods=['PATCH'],
    description='Partial updating an Exercise by ID, only by its user'
)
@extend_schema(
    methods=['DELETE'],
    description='Deleting an Exercise by ID, only by its user'
)
class ExerciseViewSet(ModelViewSet):
    """
    View sets that handle the next for the Exercise model:
    - creation of an exercise
    - updating of an exercise
    - deletion of an exercise
    - retrieving of an exercise
    """
    serializer_class = ExerciseSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = Exercise.objects.all()

    def get_serializer_class(self):
        """Handle different serializers for different actions."""
        if self.action == 'list':
            return ExerciseListSerializer
        return ExerciseSerializer

    def get_queryset(self):
        """Return exercises for the authenticated user."""
        return Exercise.objects.filter(user=self.request.user)

    @extend_schema(
        methods=['GET'],
        description="Retrieving specific Exercise by ID, only by its user."
    )
    def retrieve(self, request, *args, **kwargs):
        """wrote this only for the extent_schema"""
        return super().retrieve(request, *args, **kwargs)


class ExerciseLogViewSet(ModelViewSet):
    pass
