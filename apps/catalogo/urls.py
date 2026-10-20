from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EditoraViewSet, CategoriaViewSet, AutorViewSet, LivroViewSet, ExemplarViewSet

router = DefaultRouter()
router.register('editoras', EditoraViewSet, basename='editora')
router.register('categorias', CategoriaViewSet, basename='categoria')
router.register('autores', AutorViewSet, basename='autor')
router.register('livros', LivroViewSet, basename='livro')
router.register('exemplares', ExemplarViewSet, basename='exemplar')

urlpatterns = [
    path('', include(router.urls)),
]
