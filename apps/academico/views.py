from rest_framework import viewsets, permissions
from .models import Instituicao, Curso
from .serializers import InstituicaoSerializer, CursoSerializer

class InstituicaoViewSet(viewsets.ModelViewSet):
    """CRUD de Instituições de ensino (leitura pública, escrita autenticada)."""
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = Instituicao.objects.all().order_by('nome')
    serializer_class = InstituicaoSerializer
    search_fields = ['nome']
    ordering_fields = ['id_instituicao', 'nome']


class CursoViewSet(viewsets.ModelViewSet):
    """CRUD de Cursos acadêmicos (leitura pública, escrita autenticada)."""
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = Curso.objects.select_related('instituicao').all().order_by('nome')
    serializer_class = CursoSerializer
    search_fields = ['nome', 'instituicao__nome']
    filterset_fields = ['instituicao']
    ordering_fields = ['id_curso', 'nome']
