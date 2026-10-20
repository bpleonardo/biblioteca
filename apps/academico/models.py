from django.db import models

class Instituicao(models.Model):
    """
    Modelo de Instituição mapeado para tb_instituicao.
    """
    id_instituicao = models.AutoField(primary_key=True, db_column='id_instituicao')
    nome = models.CharField(max_length=150, db_column='nome', verbose_name='Nome')

    class Meta:
        db_table = 'tb_instituicao'
        verbose_name = 'Instituição'
        verbose_name_plural = 'Instituições'
        ordering = ['nome']

    def __str__(self):
        return self.nome


class Curso(models.Model):
    """
    Modelo de Curso mapeado para tb_curso.
    """
    id_curso = models.AutoField(primary_key=True, db_column='id_curso')
    nome = models.CharField(max_length=100, db_column='nome', verbose_name='Nome')
    instituicao = models.ForeignKey(
        Instituicao,
        on_delete=models.PROTECT,
        db_column='id_instituicao',
        related_name='cursos',
        verbose_name='Instituição'
    )

    class Meta:
        db_table = 'tb_curso'
        verbose_name = 'Curso'
        verbose_name_plural = 'Cursos'
        ordering = ['nome']

    def __str__(self):
        return f"{self.nome} - {self.instituicao.nome}"
