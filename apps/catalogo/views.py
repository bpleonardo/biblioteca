from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Editora, Categoria, Autor, Livro, Exemplar
from .serializers import (
    EditoraSerializer, CategoriaSerializer, AutorSerializer,
    LivroSerializer, ExemplarSerializer
)

class EditoraViewSet(viewsets.ModelViewSet):
    """CRUD de Editoras (leitura pública, escrita autenticada)."""
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = Editora.objects.all().order_by('nome')
    serializer_class = EditoraSerializer
    search_fields = ['nome', 'cnpj']
    ordering_fields = ['id_editora', 'nome']


class CategoriaViewSet(viewsets.ModelViewSet):
    """CRUD de Categorias de livros (leitura pública, escrita autenticada)."""
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = Categoria.objects.all().order_by('descricao')
    serializer_class = CategoriaSerializer
    search_fields = ['descricao']
    ordering_fields = ['id_categoria', 'descricao']


class AutorViewSet(viewsets.ModelViewSet):
    """CRUD de Autores (leitura pública, escrita autenticada)."""
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = Autor.objects.select_related('editora').all().order_by('nome')
    serializer_class = AutorSerializer
    search_fields = ['nome', 'email', 'cpf']
    filterset_fields = ['editora']
    ordering_fields = ['id_autor', 'nome']


class LivroViewSet(viewsets.ModelViewSet):
    """
    CRUD de Livros e Catálogo (leitura pública para consulta, escrita restrita a autenticados).
    Permite filtrar por categoria, editora, autores e buscar por título e ISBN.
    """
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = Livro.objects.select_related('categoria', 'editora').prefetch_related('autores', 'exemplares').all().order_by('titulo')
    serializer_class = LivroSerializer
    search_fields = ['titulo', 'isbn', 'autores__nome', 'editora__nome', 'categoria__descricao']
    filterset_fields = ['categoria', 'editora', 'autores']
    ordering_fields = ['id_livro', 'titulo']

    @action(detail=True, methods=['get'])
    def exemplares(self, request, pk=None):
        """Retorna todos os exemplares associados ao livro."""
        livro = self.get_object()
        exemplares = livro.exemplares.all().order_by('id_exemplar')
        serializer = ExemplarSerializer(exemplares, many=True)
        return Response(serializer.data)


class ExemplarViewSet(viewsets.ModelViewSet):
    """CRUD de Exemplares físicos de livros (leitura pública, escrita autenticada)."""
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = Exemplar.objects.select_related('livro').all().order_by('id_exemplar')
    serializer_class = ExemplarSerializer
    search_fields = ['livro__titulo', 'livro__isbn', 'edicao']
    filterset_fields = ['livro', 'situacao']
    ordering_fields = ['id_exemplar', 'situacao', 'edicao']
