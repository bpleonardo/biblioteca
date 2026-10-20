from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    # Admin Django
    path('admin/', admin.site.urls),

    # OpenAPI & Swagger UI
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),

    # REST APIs
    path('api/', include('apps.usuarios.urls')),
    path('api/', include('apps.academico.urls')),
    path('api/', include('apps.catalogo.urls')),
    path('api/', include('apps.circulacao.urls')),
    path('api/', include('apps.auditoria.urls')),

    # Frontend Views and Dashboard API
    path('', include('apps.core.urls')),
]
