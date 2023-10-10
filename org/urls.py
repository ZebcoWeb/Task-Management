from rest_framework.routers import DefaultRouter
from django.urls import path, include

from org import views

router = DefaultRouter()

router.register(r'', views.OrganizationViewSet)

urlpatterns = [
    path('', include(router.urls)),
]