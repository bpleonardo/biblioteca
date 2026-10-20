from django.contrib import admin
from .models import Instituicao, Curso

@admin.register(Instituicao)
class InstituicaoAdmin(admin.ModelAdmin):
    list_display = ('id_instituicao', 'nome')
    search_fields = ('nome',)
    ordering = ('nome',)


@admin.register(Curso)
class CursoAdmin(admin.ModelAdmin):
    list_display = ('id_curso', 'nome', 'instituicao')
    search_fields = ('nome', 'instituicao__nome')
    list_filter = ('instituicao',)
    autocomplete_fields = ('instituicao',)
    ordering = ('nome',)
