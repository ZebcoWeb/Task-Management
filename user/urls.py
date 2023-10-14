from rest_framework.routers import DefaultRouter
from django.urls import path, include

from user import views

router = DefaultRouter()


router.register(r'auth', views.DefualtViewSet)
router.register(r'user', views.UserViewSet) 

urlpatterns = [
    path('', include(router.urls)),
]

