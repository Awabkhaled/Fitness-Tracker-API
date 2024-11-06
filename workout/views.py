from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from .serializers import WorkoutLogSerializer, WorkoutLogListSerializer
from .models import WorkoutLog
from drf_spectacular.utils import extend_schema


@extend_schema(
    methods=['GET'],
    description='Retriving workout_logs related to the current loged user'
)
@extend_schema(
    methods=['POST'],
    description='Creating workout_logs with the current loged user'
)
@extend_schema(
    methods=['PUT'],
    description='Updating a workout_log by ID, only by its user'
)
@extend_schema(
    methods=['PATCH'],
    description='Partial updating a workout_log by ID, only by its user'
)
@extend_schema(
    methods=['DELETE'],
    description='Deleting a workout_log by ID, only by its user'
)
class WorkoutLogViewSet(ModelViewSet):
    """The view for handling workout endpoints:
    - Create
    - Retrieve
    - Update
    - Destroy (Delete)
    - List
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = WorkoutLog.objects.all()

    def get_serializer_class(self):
        """Handle different serializers for different actions."""
        if self.action == 'list':
            return WorkoutLogListSerializer
        return WorkoutLogSerializer

    def get_queryset(self):
        """Return workout logs for the authenticated user."""
        return WorkoutLog.objects.filter(user=self.request.user)

    @extend_schema(
        methods=['GET'],
        description="Retrieving specific workout_log by ID, only by its user."
    )
    def retrieve(self, request, *args, **kwargs):
        """wrote this only for the extent_schema"""
        return super().retrieve(request, *args, **kwargs)
