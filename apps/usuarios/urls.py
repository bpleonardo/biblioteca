from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UsuarioViewSet, AlunoViewSet, LoginAPIView, LogoutAPIView, MeAPIView

router = DefaultRouter()
router.register('usuarios', UsuarioViewSet, basename='usuario')
router.register('alunos', AlunoViewSet, basename='aluno')

urlpatterns = [
    path('auth/login/', LoginAPIView.as_view(), name='api-login'),
    path('auth/logout/', LogoutAPIView.as_view(), name='api-logout'),
    path('auth/me/', MeAPIView.as_view(), name='api-me'),
    path('', include(router.urls)),
]
