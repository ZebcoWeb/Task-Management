from rest_framework.routers import DefaultRouter
from django.urls import path, include

from user import views

router = DefaultRouter()


router.register(r'', views.DefualtAPIView)

urlpatterns = [
    path('', include(router.urls)),
]

