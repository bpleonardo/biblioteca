from datetime import date
from django.conf import settings
from django.db import models
from django.utils import timezone


class SituacaoReserva(models.TextChoices):
    PENDENTE = 'Pendente', 'Pendente'
    ATENDIDA = 'Atendida', 'Atendida'
    CANCELADA = 'Cancelada', 'Cancelada'


class Reserva(models.Model):
    """Modelo de Reserva mapeado para tb_reserva."""
    id_reserva = models.AutoField(primary_key=True, db_column='id_reserva')
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        db_column='id_usuario',
        related_name='reservas',
        verbose_name='Usuário'
    )
    livro = models.ForeignKey(
        'catalogo.Livro',
        on_delete=models.CASCADE,
        db_column='id_livro',
        related_name='reservas',
        verbose_name='Livro'
    )
    data_reserva = models.DateField(
        default=timezone.now,
        db_column='data_reserva',
        verbose_name='Data da Reserva'
    )
    situacao = models.CharField(
        max_length=30,
        choices=SituacaoReserva.choices,
        default=SituacaoReserva.PENDENTE,
        db_column='situacao',
        verbose_name='Situação'
    )

    class Meta:
        db_table = 'tb_reserva'
        verbose_name = 'Reserva'
        verbose_name_plural = 'Reservas'
        ordering = ['-data_reserva', '-id_reserva']

    def __str__(self):
        return f"Reserva #{self.id_reserva} - {self.livro.titulo} para {self.usuario.nome} ({self.situacao})"


class Emprestimo(models.Model):
    """Modelo de Empréstimo mapeado para tb_emprestimo."""
    id_emprestimo = models.AutoField(primary_key=True, db_column='id_emprestimo')
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        db_column='id_usuario',
        related_name='emprestimos',
        verbose_name='Usuário'
    )
    data_emprestimo = models.DateField(
        default=timezone.now,
        db_column='data_emprestimo',
        verbose_name='Data do Empréstimo'
    )
    data_prevista_devolucao = models.DateField(
        blank=True,
        null=True,
        db_column='data_prevista_devolucao',
        verbose_name='Previsão de Devolução'
    )
    data_devolucao = models.DateField(
        blank=True,
        null=True,
        db_column='data_devolucao',
        verbose_name='Data de Devolução'
    )

    class Meta:
        db_table = 'tb_emprestimo'
        verbose_name = 'Empréstimo'
        verbose_name_plural = 'Empréstimos'
        ordering = ['-data_emprestimo', '-id_emprestimo']

    def __str__(self):
        status = "Devolvido" if self.data_devolucao else "Ativo"
        return f"Empréstimo #{self.id_emprestimo} - {self.usuario.nome} ({status})"

    @property
    def is_ativo(self):
        return self.data_devolucao is None

    @property
    def is_atrasado(self):
        if not self.data_devolucao and self.data_prevista_devolucao:
            return date.today() > self.data_prevista_devolucao
        return False


class ItemEmprestimo(models.Model):
    """Modelo de Item de Empréstimo mapeado para tb_item_emprestimo."""
    id_item_emprestimo = models.AutoField(primary_key=True, db_column='id_item_emprestimo')
    emprestimo = models.ForeignKey(
        Emprestimo,
        on_delete=models.CASCADE,
        db_column='id_emprestimo',
        related_name='itens',
        verbose_name='Empréstimo'
    )
    exemplar = models.ForeignKey(
        'catalogo.Exemplar',
        on_delete=models.PROTECT,
        db_column='id_exemplar',
        related_name='itens_emprestimo',
        verbose_name='Exemplar'
    )

    class Meta:
        db_table = 'tb_item_emprestimo'
        verbose_name = 'Item de Empréstimo'
        verbose_name_plural = 'Itens de Empréstimo'

    def __str__(self):
        return f"Item #{self.id_item_emprestimo} - Exemplar #{self.exemplar_id} (Empréstimo #{self.emprestimo_id})"
