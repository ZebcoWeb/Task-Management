from django.contrib import admin
from django.urls import path, include

from drf_yasg.views import get_schema_view
from drf_yasg import openapi



schema_view = get_schema_view(
   openapi.Info(
      title="Task Manager API",
      default_version='v1',
   )
)


urlpatterns = [
   path('docs/', schema_view.with_ui('swagger', cache_timeout=0)),
   path('redoc/', schema_view.with_ui('redoc', cache_timeout=0)),
   path("admin/", admin.site.urls),
   
   path("users/", include("user.urls")),
   path("tasks/", include("task.urls")),
   path("orgs/", include("org.urls")),
   path("requests/", include("request.urls")),
]
