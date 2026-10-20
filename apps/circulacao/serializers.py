from datetime import date
from rest_framework import serializers
from .models import Reserva, Emprestimo, ItemEmprestimo
from apps.catalogo.serializers import ExemplarSerializer
from apps.usuarios.serializers import UsuarioSerializer

class ReservaSerializer(serializers.ModelSerializer):
    usuario_nome = serializers.CharField(source='usuario.nome', read_only=True)
    usuario_email = serializers.CharField(source='usuario.email', read_only=True)
    livro_titulo = serializers.CharField(source='livro.titulo', read_only=True)

    class Meta:
        model = Reserva
        fields = [
            'id_reserva', 'usuario', 'usuario_nome', 'usuario_email',
            'livro', 'livro_titulo', 'data_reserva', 'situacao'
        ]
        read_only_fields = ['id_reserva', 'data_reserva', 'situacao']


class CriarReservaSerializer(serializers.Serializer):
    usuario_id = serializers.IntegerField(required=True)
    livro_id = serializers.IntegerField(required=True)


class ItemEmprestimoSerializer(serializers.ModelSerializer):
    exemplar_detalhes = ExemplarSerializer(source='exemplar', read_only=True)

    class Meta:
        model = ItemEmprestimo
        fields = ['id_item_emprestimo', 'exemplar', 'exemplar_detalhes']


class EmprestimoSerializer(serializers.ModelSerializer):
    usuario_nome = serializers.CharField(source='usuario.nome', read_only=True)
    usuario_email = serializers.CharField(source='usuario.email', read_only=True)
    itens = ItemEmprestimoSerializer(many=True, read_only=True)
    is_ativo = serializers.BooleanField(read_only=True)
    is_atrasado = serializers.BooleanField(read_only=True)

    class Meta:
        model = Emprestimo
        fields = [
            'id_emprestimo', 'usuario', 'usuario_nome', 'usuario_email',
            'data_emprestimo', 'data_prevista_devolucao', 'data_devolucao',
            'is_ativo', 'is_atrasado', 'itens'
        ]
        read_only_fields = ['id_emprestimo', 'data_emprestimo', 'data_devolucao', 'itens']


class CriarEmprestimoSerializer(serializers.Serializer):
    usuario_id = serializers.IntegerField(required=True)
    exemplar_ids = serializers.ListField(
        child=serializers.IntegerField(),
        allow_empty=False,
        required=True
    )
    data_prevista_devolucao = serializers.DateField(required=True)
