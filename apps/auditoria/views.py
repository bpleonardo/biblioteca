from rest_framework import viewsets, permissions
from .models import LogSistema
from .serializers import LogSistemaSerializer

class LogSistemaViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Consulta de logs do sistema (somente leitura, restrito a usuários autenticados).
    """
    permission_classes = [permissions.IsAuthenticated]
    queryset = LogSistema.objects.all().order_by('-data_registro', '-id_log')
    serializer_class = LogSistemaSerializer
    search_fields = ['descricao', 'id_aluno']
    filterset_fields = ['id_aluno']
    ordering_fields = ['id_log', 'data_registro']
