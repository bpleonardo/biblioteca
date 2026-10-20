from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import InstituicaoViewSet, CursoViewSet

router = DefaultRouter()
router.register('instituicoes', InstituicaoViewSet, basename='instituicao')
router.register('cursos', CursoViewSet, basename='curso')

urlpatterns = [
    path('', include(router.urls)),
]
