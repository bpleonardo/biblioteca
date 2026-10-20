from django.db import models
from django.utils import timezone

class LogSistema(models.Model):
    """
    Modelo de Log mapeado para tb_log_sistema.
    Preserva a particularidade original: coluna id_aluno armazena o id_usuario fornecido no evento.
    Sem chave estrangeira para essa coluna, conforme modelagem original.
    """
    id_log = models.AutoField(primary_key=True, db_column='id_log')
    id_aluno = models.DecimalField(
        max_digits=10,
        decimal_places=0,
        blank=True,
        null=True,
        db_column='id_aluno',
        verbose_name='ID Usuário / Aluno'
    )
    descricao = models.CharField(
        max_length=120,
        blank=True,
        null=True,
        db_column='descricao',
        verbose_name='Descrição / Evento'
    )
    data_registro = models.DateTimeField(
        default=timezone.now,
        db_column='data_registro',
        verbose_name='Data de Registro'
    )

    class Meta:
        db_table = 'tb_log_sistema'
        verbose_name = 'Log do Sistema'
        verbose_name_plural = 'Logs do Sistema'
        ordering = ['-data_registro', '-id_log']

    def __str__(self):
        return f"Log #{self.id_log} - [{self.data_registro:%d/%m/%Y %H:%M:%S}] {self.descricao}"
