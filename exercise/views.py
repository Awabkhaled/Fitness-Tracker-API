from rest_framework.generics import ListAPIView, GenericAPIView
from rest_framework.viewsets import ModelViewSet
from exercise.models import Exercise, ExerciseLog
from exercise.serializers import (
    ExerciseLogSerializer,
    ExerciseSerializer,
    ExerciseListSerializer,
    ExerciseSearchSerializer,
    ExerciseLogProgressListSerializer)
from rest_framework.serializers import ValidationError
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
import re
from django.core.exceptions import ValidationError as VE
from exercise.validators import validate_exercise_name
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework.response import Response


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
        return Exercise.objects.filter(user=self.request.user).order_by('-created_at') # does not work noqa

    @extend_schema(
        methods=['GET'],
        description="Retrieving specific Exercise by ID, only by its user."
    )
    def retrieve(self, request, *args, **kwargs):
        """wrote this only for the extent_schema"""
        return super().retrieve(request, *args, **kwargs)


@extend_schema(
    methods=['GET'],
    description='Retriving Exercise_logs related to the current loged user'
)
@extend_schema(
    methods=['POST'],
    description='Creating Exercise_log with the current loged user'
)
@extend_schema(
    methods=['PUT'],
    description='Updating an Exercise_log by ID, only by its user'
)
@extend_schema(
    methods=['PATCH'],
    description='Partial updating an Exercise_log by ID, only by its user'
)
@extend_schema(
    methods=['DELETE'],
    description='Deleting an Exercise_log by ID, only by its user'
)
class ExerciseLogViewSet(ModelViewSet):
    serializer_class = ExerciseLogSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = ExerciseLog.objects.all()

    def get_queryset(self):
        """Return exercises for the authenticated user."""
        return ExerciseLog.objects.filter(user=self.request.user)

    @extend_schema(
        methods=['GET'],
        description="Retrieving specific Exercise_log by ID, only by its user."
    )
    def retrieve(self, request, *args, **kwargs):
        """wrote this only for the extent_schema"""
        return super().retrieve(request, *args, **kwargs)


@extend_schema(
    parameters=[
        OpenApiParameter(
            name="name",
            type=str,
            location=OpenApiParameter.QUERY,
            description="Name of the exercise to search for",
            required=False,
        ),
    ]
)
class ExerciseSearchView(ListAPIView):
    """
    searching for an exercise by parameters
    - For the name search: search for the exercise that contain this name
    in their name
    - used in endpoint to search about exercise while writing
    in the exercise log by name
    - or used in the regular search
    - currently uses name only in the future will handle
    other parameters if added
    """
    serializer_class = ExerciseListSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Filter execise by search filters
        """
        # extract user so I can ensuring that only user exercises is returned
        user = self.request.user
        query = Q()

        # validate parameters
        search_params_serializer = ExerciseSearchSerializer(
            data=self.request.query_params)
        search_params_serializer.is_valid(raise_exception=True)
        search_params = search_params_serializer.validated_data

        if search_params:
            # Filter based on validated search parameters
            name = search_params.pop('name', None)
            if name:
                try:
                    name = re.sub(r'\s+', ' ', name.strip())
                    validate_exercise_name(name)
                    query &= Q(name__icontains=name)
                except VE:
                    pass
            for key, value in search_params.items():
                query &= Q(**{f"{key}": f"{value}"})
            if len(query) < 1:
                return []
            query &= Q(user=user)
            exercises = Exercise.objects.filter(query)
            exercises = list(Exercise.objects.filter(query))
            if exercises:
                exercises = \
                    sorted(exercises, key=lambda exercise: len(exercise.name))
            return exercises

        else:
            raise ValidationError("Parameters empty or invalid")


@extend_schema(
    parameters=[
        OpenApiParameter(
            name="exercise_id",
            type=int,
            location=OpenApiParameter.QUERY,
            description="id of the exercise to see the progress for",
            required=True,
        ),
    ]
)
class ExerciseProgressView(GenericAPIView):
    """
    endpoint to return the progress of an exercise
    - it takes an id for an exercise and returns list
    of exercise logs with same user and erexrcise but
    different workout logs, with some info serialized
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        returns all exercise logs with the same user and exercise
        """
        # Check if exercise_id is provided
        exercise_id = request.GET.get('exercise_id')
        if not exercise_id:
            return Response({"Error": "Exercise id is required."}, status=400)

        # Validate that exercise_id is a positive integer
        try:
            exercise_id = int(exercise_id)
            if exercise_id <= 0:
                return Response(
                    {"Error": "Exercise ID must be a positive integer."},
                    status=400)
        except ValueError:
            return Response(
                {"Error": "Exercise ID must be a valid integer."}, status=400)


        # Get the instance
        try:
            exercise = Exercise.objects.get(id=exercise_id, user=request.user)
        except Exercise.DoesNotExist:
            return Response({"detail": "Exercise not found."}, status=404)

        # get the ExerciseLogs for the specified exercise and user
        exercise_logs = ExerciseLog.objects.filter(
            exercise=exercise,
            user=request.user
        ).order_by('created_at')

        # Serialize the logs
        serialized_logs = ExerciseLogProgressListSerializer(exercise_logs,
                                                            many=True)

        return Response({
            "exercise_id": exercise.id,
            "exercise_name": exercise.name,
            "progress_logs": serialized_logs.data
        })
