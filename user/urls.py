"""User related endpoints"""
from django.urls import path
from . import views
app_name = 'user'

urlpatterns = [
    path('signup/', views.CreateUserAPIView.as_view(),
         name='create'),
    path('signin/', views.AuthUserView.as_view(),
         name='token_obtain'),
    path('get_update/', views.UpdateRetriveUserView.as_view(),
         name='get_update'),
]
