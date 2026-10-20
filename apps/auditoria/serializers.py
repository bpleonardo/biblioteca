from rest_framework import serializers
from .models import LogSistema

class LogSistemaSerializer(serializers.ModelSerializer):
    class Meta:
        model = LogSistema
        fields = ['id_log', 'id_aluno', 'descricao', 'data_registro']
        read_only_fields = ['id_log', 'id_aluno', 'descricao', 'data_registro']
