from django.urls import (
    path,
    include
)
from .views import WorkoutLogViewSet
from rest_framework.routers import DefaultRouter
app_name = 'workout'
router = DefaultRouter()
router.register('workout_log', WorkoutLogViewSet)

urlpatterns = [
    path('', include(router.urls))
]
