from django.db import models

class Editora(models.Model):
    """Modelo de Editora mapeado para tb_editora."""
    id_editora = models.AutoField(primary_key=True, db_column='id_editora')
    nome = models.CharField(max_length=100, db_column='nome', verbose_name='Nome')
    cnpj = models.CharField(max_length=18, blank=True, null=True, db_column='cnpj', verbose_name='CNPJ')

    class Meta:
        db_table = 'tb_editora'
        verbose_name = 'Editora'
        verbose_name_plural = 'Editoras'
        ordering = ['nome']

    def __str__(self):
        return self.nome


class Categoria(models.Model):
    """Modelo de Categoria mapeado para tb_categoria."""
    id_categoria = models.AutoField(primary_key=True, db_column='id_categoria')
    descricao = models.CharField(max_length=100, db_column='descricao', verbose_name='Descrição')

    class Meta:
        db_table = 'tb_categoria'
        verbose_name = 'Categoria'
        verbose_name_plural = 'Categorias'
        ordering = ['descricao']

    def __str__(self):
        return self.descricao


class Autor(models.Model):
    """Modelo de Autor mapeado para tb_autores."""
    id_autor = models.AutoField(primary_key=True, db_column='id_autor')
    nome = models.CharField(max_length=100, db_column='nome', verbose_name='Nome')
    email = models.CharField(max_length=150, blank=True, null=True, db_column='email', verbose_name='E-mail')
    cpf = models.CharField(max_length=14, blank=True, null=True, db_column='cpf', verbose_name='CPF')
    celular = models.CharField(max_length=20, blank=True, null=True, db_column='celular', verbose_name='Celular')
    editora = models.ForeignKey(
        Editora,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        db_column='id_editora',
        related_name='autores',
        verbose_name='Editora'
    )

    class Meta:
        db_table = 'tb_autores'
        verbose_name = 'Autor'
        verbose_name_plural = 'Autores'
        ordering = ['nome']

    def __str__(self):
        return self.nome


class Livro(models.Model):
    """Modelo de Livro mapeado para tb_livros."""
    id_livro = models.AutoField(primary_key=True, db_column='id_livro')
    titulo = models.CharField(max_length=200, db_column='titulo', verbose_name='Título')
    isbn = models.CharField(max_length=20, blank=True, null=True, db_column='isbn', verbose_name='ISBN')
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.PROTECT,
        db_column='id_categoria',
        related_name='livros',
        verbose_name='Categoria'
    )
    editora = models.ForeignKey(
        Editora,
        on_delete=models.PROTECT,
        db_column='id_editora',
        related_name='livros',
        verbose_name='Editora'
    )
    autores = models.ManyToManyField(
        Autor,
        through='LivroAutor',
        related_name='livros',
        verbose_name='Autores'
    )

    class Meta:
        db_table = 'tb_livros'
        verbose_name = 'Livro'
        verbose_name_plural = 'Livros'
        ordering = ['titulo']

    def __str__(self):
        return self.titulo


class LivroAutor(models.Model):
    """
    Tabela associativa N:N tb_livros_autores com chave primária composta (id_livro, id_autor).
    Preserva a estrutura física original sem criar campo identificador artificial.
    """
    pk = models.CompositePrimaryKey('livro', 'autor')
    livro = models.ForeignKey(Livro, on_delete=models.CASCADE, db_column='id_livro', verbose_name='Livro')
    autor = models.ForeignKey(Autor, on_delete=models.CASCADE, db_column='id_autor', verbose_name='Autor')

    class Meta:
        db_table = 'tb_livros_autores'
        verbose_name = 'Autor do Livro'
        verbose_name_plural = 'Autores dos Livros'

    def __str__(self):
        return f"{self.livro.titulo} - {self.autor.nome}"


class SituacaoExemplar(models.TextChoices):
    DISPONIVEL = 'Disponível', 'Disponível'
    EMPRESTADO = 'Emprestado', 'Emprestado'
    INDISPONIVEL = 'Indisponível', 'Indisponível'


class Exemplar(models.Model):
    """Modelo de Exemplar físico mapeado para tb_exemplares."""
    id_exemplar = models.AutoField(primary_key=True, db_column='id_exemplar')
    livro = models.ForeignKey(
        Livro,
        on_delete=models.CASCADE,
        db_column='id_livro',
        related_name='exemplares',
        verbose_name='Livro'
    )
    edicao = models.CharField(max_length=30, blank=True, null=True, db_column='edicao', verbose_name='Edição')
    situacao = models.CharField(
        max_length=30,
        choices=SituacaoExemplar.choices,
        default=SituacaoExemplar.DISPONIVEL,
        db_column='situacao',
        verbose_name='Situação'
    )

    class Meta:
        db_table = 'tb_exemplares'
        verbose_name = 'Exemplar'
        verbose_name_plural = 'Exemplares'
        ordering = ['livro__titulo', 'id_exemplar']

    def __str__(self):
        return f"Exemplar #{self.id_exemplar} - {self.livro.titulo} ({self.situacao})"
