from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from .serializers import WorkoutLogSerializer, WorkoutLogListSerializer
from .models import WorkoutLog

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

    def get_serializer_class(self):
        """Handle different serializers for different actions."""
        if self.action == 'list':
            return WorkoutLogListSerializer
        return WorkoutLogSerializer

    def get_queryset(self):
        """Return workout logs for the authenticated user."""
        return WorkoutLog.objects.filter(user=self.request.user)
