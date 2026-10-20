from django.contrib import admin
from .models import LogSistema

@admin.register(LogSistema)
class LogSistemaAdmin(admin.ModelAdmin):
    list_display = ('id_log', 'data_registro', 'id_aluno', 'descricao')
    list_filter = ('data_registro',)
    search_fields = ('descricao', 'id_aluno')
    ordering = ('-data_registro', '-id_log')
    readonly_fields = ('id_log', 'id_aluno', 'descricao', 'data_registro')

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
