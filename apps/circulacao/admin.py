from django.contrib import admin
from .models import Reserva, Emprestimo, ItemEmprestimo

@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ('id_reserva', 'livro', 'usuario', 'data_reserva', 'situacao')
    search_fields = ('livro__titulo', 'usuario__nome', 'usuario__email')
    list_filter = ('situacao', 'data_reserva')
    autocomplete_fields = ('usuario', 'livro')
    ordering = ('-data_reserva', '-id_reserva')


class ItemEmprestimoInline(admin.TabularInline):
    model = ItemEmprestimo
    extra = 0
    autocomplete_fields = ('exemplar',)
    readonly_fields = ('exemplar',)
    can_delete = False


@admin.register(Emprestimo)
class EmprestimoAdmin(admin.ModelAdmin):
    list_display = ('id_emprestimo', 'usuario', 'data_emprestimo', 'data_prevista_devolucao', 'data_devolucao', 'status_formatado')
    search_fields = ('usuario__nome', 'usuario__email')
    list_filter = ('data_emprestimo', 'data_devolucao')
    autocomplete_fields = ('usuario',)
    inlines = [ItemEmprestimoInline]
    ordering = ('-data_emprestimo', '-id_emprestimo')

    def status_formatado(self, obj):
        if obj.data_devolucao:
            return f"Devolvido em {obj.data_devolucao:%d/%m/%Y}"
        if obj.is_atrasado:
            return "Em atraso"
        return "Ativo"
    status_formatado.short_description = "Status"
