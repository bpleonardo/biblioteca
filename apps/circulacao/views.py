from datetime import date
from django.core.exceptions import ValidationError
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from .models import Reserva, Emprestimo, SituacaoReserva
from .serializers import (
    ReservaSerializer, CriarReservaSerializer,
    EmprestimoSerializer, CriarEmprestimoSerializer
)
from .services import (
    criar_emprestimo, devolver_emprestimo,
    criar_reserva, cancelar_reserva, atender_reserva
)

class ReservaViewSet(viewsets.ModelViewSet):
    """
    Gerenciamento de Reservas de livros (acesso restrito a usuários autenticados).
    """
    permission_classes = [permissions.IsAuthenticated]
    queryset = Reserva.objects.select_related('usuario', 'livro').all().order_by('-data_reserva', '-id_reserva')
    serializer_class = ReservaSerializer
    filterset_fields = ['usuario', 'livro', 'situacao']
    search_fields = ['usuario__nome', 'usuario__email', 'livro__titulo']
    ordering_fields = ['id_reserva', 'data_reserva', 'situacao']

    @extend_schema(request=CriarReservaSerializer, responses={201: ReservaSerializer})
    def create(self, request, *args, **kwargs):
        serializer = CriarReservaSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            reserva = criar_reserva(
                usuario_id=serializer.validated_data['usuario_id'],
                livro_id=serializer.validated_data['livro_id']
            )
            return Response(ReservaSerializer(reserva).data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response({'erro': e.message if hasattr(e, 'message') else str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def cancelamento(self, request, pk=None):
        """Cancela uma reserva existente pendente."""
        try:
            reserva = cancelar_reserva(pk)
            return Response(ReservaSerializer(reserva).data, status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response({'erro': e.message if hasattr(e, 'message') else str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def atendimento(self, request, pk=None):
        """Atende uma reserva pendente."""
        try:
            reserva = atender_reserva(pk)
            return Response(ReservaSerializer(reserva).data, status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response({'erro': e.message if hasattr(e, 'message') else str(e)}, status=status.HTTP_400_BAD_REQUEST)


class EmprestimoViewSet(viewsets.ModelViewSet):
    """
    Gerenciamento de Empréstimos e Devoluções (acesso restrito a usuários autenticados).
    """
    permission_classes = [permissions.IsAuthenticated]
    queryset = Emprestimo.objects.select_related('usuario').prefetch_related('itens__exemplar__livro').all().order_by('-data_emprestimo', '-id_emprestimo')
    serializer_class = EmprestimoSerializer
    filterset_fields = ['usuario', 'data_emprestimo', 'data_devolucao']
    search_fields = ['usuario__nome', 'usuario__email']
    ordering_fields = ['id_emprestimo', 'data_emprestimo', 'data_prevista_devolucao']

    @extend_schema(request=CriarEmprestimoSerializer, responses={201: EmprestimoSerializer})
    def create(self, request, *args, **kwargs):
        serializer = CriarEmprestimoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            emprestimo = criar_emprestimo(
                usuario_id=serializer.validated_data['usuario_id'],
                exemplar_ids=serializer.validated_data['exemplar_ids'],
                data_prevista_devolucao=serializer.validated_data['data_prevista_devolucao']
            )
            return Response(EmprestimoSerializer(emprestimo).data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response({'erro': e.message if hasattr(e, 'message') else str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def devolucao(self, request, pk=None):
        """Realiza a devolução de todos os exemplares de um empréstimo."""
        try:
            emprestimo = devolver_emprestimo(pk)
            return Response(EmprestimoSerializer(emprestimo).data, status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response({'erro': e.message if hasattr(e, 'message') else str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def atrasados(self, request):
        """Lista todos os empréstimos ativos em atraso."""
        hoje = date.today()
        atrasados = self.queryset.filter(data_devolucao__isnull=True, data_prevista_devolucao__lt=hoje)
        page = self.paginate_queryset(atrasados)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(atrasados, many=True)
        return Response(serializer.data)
