from rest_framework.routers import DefaultRouter
from django.urls import path, include

from task import views

router = DefaultRouter()

router.register(r'', views.TaskViewSet)

urlpatterns = [
    path('', include(router.urls)),
]