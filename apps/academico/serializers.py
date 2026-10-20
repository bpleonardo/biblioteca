from rest_framework import serializers
from .models import Instituicao, Curso

class InstituicaoSerializer(serializers.ModelSerializer):
    total_cursos = serializers.IntegerField(source='cursos.count', read_only=True)

    class Meta:
        model = Instituicao
        fields = ['id_instituicao', 'nome', 'total_cursos']
        read_only_fields = ['id_instituicao']


class CursoSerializer(serializers.ModelSerializer):
    instituicao_nome = serializers.CharField(source='instituicao.nome', read_only=True)

    class Meta:
        model = Curso
        fields = ['id_curso', 'nome', 'instituicao', 'instituicao_nome']
        read_only_fields = ['id_curso']
