from rest_framework import serializers
from .models import Editora, Categoria, Autor, Livro, LivroAutor, Exemplar, SituacaoExemplar

class EditoraSerializer(serializers.ModelSerializer):
    class Meta:
        model = Editora
        fields = ['id_editora', 'nome', 'cnpj']
        read_only_fields = ['id_editora']


class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ['id_categoria', 'descricao']
        read_only_fields = ['id_categoria']


class AutorSerializer(serializers.ModelSerializer):
    editora_nome = serializers.CharField(source='editora.nome', read_only=True)

    class Meta:
        model = Autor
        fields = ['id_autor', 'nome', 'email', 'cpf', 'celular', 'editora', 'editora_nome']
        read_only_fields = ['id_autor']


class ExemplarSerializer(serializers.ModelSerializer):
    livro_titulo = serializers.CharField(source='livro.titulo', read_only=True)

    class Meta:
        model = Exemplar
        fields = ['id_exemplar', 'livro', 'livro_titulo', 'edicao', 'situacao']
        read_only_fields = ['id_exemplar']


class LivroAutorNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Autor
        fields = ['id_autor', 'nome', 'email']


class LivroSerializer(serializers.ModelSerializer):
    autores_ids = serializers.PrimaryKeyRelatedField(
        queryset=Autor.objects.all(),
        many=True,
        write_only=True,
        source='autores',
        required=False
    )
    autores_detalhes = LivroAutorNestedSerializer(source='autores', many=True, read_only=True)
    categoria_descricao = serializers.CharField(source='categoria.descricao', read_only=True)
    editora_nome = serializers.CharField(source='editora.nome', read_only=True)
    total_exemplares = serializers.SerializerMethodField(read_only=True)
    exemplares_disponiveis = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Livro
        fields = [
            'id_livro', 'titulo', 'isbn', 'categoria', 'categoria_descricao',
            'editora', 'editora_nome', 'autores_ids', 'autores_detalhes',
            'total_exemplares', 'exemplares_disponiveis'
        ]
        read_only_fields = ['id_livro']

    def get_total_exemplares(self, obj):
        return obj.exemplares.count()

    def get_exemplares_disponiveis(self, obj):
        return obj.exemplares.filter(situacao=SituacaoExemplar.DISPONIVEL).count()

    def create(self, validated_data):
        autores = validated_data.pop('autores', [])
        livro = Livro.objects.create(**validated_data)
        if autores:
            livro.autores.set(autores)
        return livro

    def update(self, instance, validated_data):
        autores = validated_data.pop('autores', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if autores is not None:
            instance.autores.set(autores)
        return instance
