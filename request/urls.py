from rest_framework.routers import DefaultRouter
from django.urls import path, include

from request import views

router = DefaultRouter()

router.register(r'', views.RequestViewSet)

urlpatterns = [
    path('', include(router.urls)),
]