from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg import openapi
from drf_yasg.views import get_schema_view

schema_view = get_schema_view(
    openapi.Info(
        title='Stackdump',
        default_version='v1',
        description='A Stackoverflow clone usign DRF.',
        contact=openapi.Contact(email='renan.modenese@gmail.com'),
        license=openapi.License(name='MIT License'),
    ),
    public=True,
    permission_classes=[permissions.AllowAny]
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('search/', include('search.urls')),
    path('users/', include('users.urls')),
    # Third party
    path('comments/', include('django_comments.urls')),
    path('markdownx/', include('markdownx.urls')),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

