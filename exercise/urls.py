from django.urls import (
    path,
    include
)
from .views import ExerciseViewSet, ExerciseLogViewSet # noqa
from rest_framework.routers import DefaultRouter
app_name = 'exercise'
router = DefaultRouter()
router.register('exercise', ExerciseViewSet)
# router.register('exercise_log', ExerciseLogViewSet)

urlpatterns = [
    path('', include(router.urls))
]
