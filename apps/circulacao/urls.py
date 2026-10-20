from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ReservaViewSet, EmprestimoViewSet

router = DefaultRouter()
router.register('reservas', ReservaViewSet, basename='reserva')
router.register('emprestimos', EmprestimoViewSet, basename='emprestimo')

urlpatterns = [
    path('', include(router.urls)),
]
