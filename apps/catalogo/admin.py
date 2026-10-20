from django.contrib import admin
from .models import Editora, Categoria, Autor, Livro, LivroAutor, Exemplar

@admin.register(Editora)
class EditoraAdmin(admin.ModelAdmin):
    list_display = ('id_editora', 'nome', 'cnpj')
    search_fields = ('nome', 'cnpj')
    ordering = ('nome',)


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('id_categoria', 'descricao')
    search_fields = ('descricao',)
    ordering = ('descricao',)


@admin.register(Autor)
class AutorAdmin(admin.ModelAdmin):
    list_display = ('id_autor', 'nome', 'email', 'cpf', 'editora')
    search_fields = ('nome', 'email', 'cpf')
    list_filter = ('editora',)
    autocomplete_fields = ('editora',)
    ordering = ('nome',)


class LivroAutorInline(admin.TabularInline):
    model = LivroAutor
    extra = 1
    autocomplete_fields = ('autor',)


class ExemplarInline(admin.TabularInline):
    model = Exemplar
    extra = 1
    fields = ('edicao', 'situacao')


@admin.register(Livro)
class LivroAdmin(admin.ModelAdmin):
    list_display = ('id_livro', 'titulo', 'isbn', 'categoria', 'editora', 'total_exemplares')
    search_fields = ('titulo', 'isbn', 'autores__nome')
    list_filter = ('categoria', 'editora')
    autocomplete_fields = ('categoria', 'editora')
    inlines = [LivroAutorInline, ExemplarInline]
    ordering = ('titulo',)

    def total_exemplares(self, obj):
        return obj.exemplares.count()
    total_exemplares.short_description = "Total de Exemplares"


@admin.register(Exemplar)
class ExemplarAdmin(admin.ModelAdmin):
    list_display = ('id_exemplar', 'livro', 'edicao', 'situacao')
    search_fields = ('livro__titulo', 'livro__isbn', 'edicao')
    list_filter = ('situacao', 'livro__categoria')
    autocomplete_fields = ('livro',)
    ordering = ('livro__titulo', 'id_exemplar')
