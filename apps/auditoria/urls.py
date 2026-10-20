from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LogSistemaViewSet

router = DefaultRouter()
router.register('logs', LogSistemaViewSet, basename='log')

urlpatterns = [
    path('', include(router.urls)),
]
