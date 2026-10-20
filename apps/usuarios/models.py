from django.contrib.auth.models import AbstractBaseUser
from django.db import models
from .managers import UsuarioManager

class Usuario(AbstractBaseUser):
    """
    Modelo de Usuário mapeado para a tabela física tb_usuario.
    Preserva as 4 colunas originais: id_usuario, nome, email, senha.
    """
    id_usuario = models.AutoField(primary_key=True, db_column='id_usuario')
    nome = models.CharField(max_length=100, db_column='nome')
    email = models.EmailField(max_length=150, unique=True, db_column='email')
    password = models.CharField(max_length=255, db_column='senha')

    # Desativa last_login do AbstractBaseUser para preservar estritamente as colunas de tb_usuario
    last_login = None

    objects = UsuarioManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nome']

    class Meta:
        db_table = 'tb_usuario'
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'
        ordering = ['nome']

    def __str__(self):
        return f"{self.nome} ({self.email})"

    # Compatibilidade com Django Admin sem colunas extras no banco
    @property
    def is_staff(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_superuser(self):
        return True

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True


class Aluno(models.Model):
    """
    Modelo de Aluno mapeado para a tabela física tb_aluno.
    """
    id_aluno = models.AutoField(primary_key=True, db_column='id_aluno')
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        db_column='id_usuario',
        related_name='alunos',
        verbose_name='Usuário'
    )
    curso = models.ForeignKey(
        'academico.Curso',
        on_delete=models.PROTECT,
        db_column='id_curso',
        related_name='alunos',
        verbose_name='Curso'
    )
    matricula = models.CharField(
        max_length=30,
        blank=True,
        null=True,
        db_column='matricula',
        verbose_name='Matrícula'
    )

    class Meta:
        db_table = 'tb_aluno'
        verbose_name = 'Aluno'
        verbose_name_plural = 'Alunos'
        ordering = ['usuario__nome']

    def __str__(self):
        return f"{self.usuario.nome} - {self.curso.nome} ({self.matricula or 'Sem matrícula'})"
