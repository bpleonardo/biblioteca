from rest_framework import serializers
from .models import Usuario, Aluno
from apps.academico.models import Curso

class UsuarioSerializer(serializers.ModelSerializer):
    senha = serializers.CharField(write_only=True, required=False, min_length=6)

    class Meta:
        model = Usuario
        fields = ['id_usuario', 'nome', 'email', 'senha']
        read_only_fields = ['id_usuario']

    def create(self, validated_data):
        senha = validated_data.pop('senha', None)
        usuario = Usuario(**validated_data)
        if senha:
            usuario.set_password(senha)
        else:
            usuario.set_unusable_password()
        usuario.save()
        return usuario

    def update(self, instance, validated_data):
        senha = validated_data.pop('senha', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if senha:
            instance.set_password(senha)
        instance.save()
        return instance


class AlunoSerializer(serializers.ModelSerializer):
    usuario_detalhes = serializers.SerializerMethodField(read_only=True)
    curso_detalhes = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Aluno
        fields = ['id_aluno', 'usuario', 'curso', 'matricula', 'usuario_detalhes', 'curso_detalhes']
        read_only_fields = ['id_aluno']

    def get_usuario_detalhes(self, obj):
        return {
            'id_usuario': obj.usuario.id_usuario,
            'nome': obj.usuario.nome,
            'email': obj.usuario.email
        }

    def get_curso_detalhes(self, obj):
        return {
            'id_curso': obj.curso.id_curso,
            'nome': obj.curso.nome,
            'instituicao': obj.curso.instituicao.nome
        }


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    senha = serializers.CharField(write_only=True)
