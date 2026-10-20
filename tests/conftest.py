import pytest
from rest_framework.test import APIClient
from apps.usuarios.models import Usuario, Aluno
from apps.academico.models import Instituicao, Curso
from apps.catalogo.models import (
    Editora, Categoria, Autor, Livro, Exemplar, SituacaoExemplar
)

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def instituicao(db):
    return Instituicao.objects.create(nome="Universidade Teste")

@pytest.fixture
def curso(db, instituicao):
    return Curso.objects.create(nome="Engenharia de Software", instituicao=instituicao)

@pytest.fixture
def usuario(db):
    user = Usuario.objects.create_user(
        email="leitor@teste.com",
        nome="Leitor Teste",
        password="segredo_teste"
    )
    return user

@pytest.fixture
def aluno(db, usuario, curso):
    return Aluno.objects.create(
        usuario=usuario,
        curso=curso,
        matricula="TEST-2024-001"
    )

@pytest.fixture
def editora(db):
    return Editora.objects.create(nome="Editora Alpha", cnpj="11.222.333/0001-44")

@pytest.fixture
def categoria(db):
    return Categoria.objects.create(descricao="Tecnologia da Informação")

@pytest.fixture
def autores(db, editora):
    a1 = Autor.objects.create(nome="Autor Um", email="a1@teste.com", editora=editora)
    a2 = Autor.objects.create(nome="Autor Dois", email="a2@teste.com", editora=editora)
    return [a1, a2]

@pytest.fixture
def livro(db, categoria, editora, autores):
    l = Livro.objects.create(
        titulo="Arquitetura de Software Moderna",
        isbn="978-1234567890",
        categoria=categoria,
        editora=editora
    )
    l.autores.set(autores)
    return l

@pytest.fixture
def exemplares(db, livro):
    ex1 = Exemplar.objects.create(livro=livro, edicao="1ª Edição", situacao=SituacaoExemplar.DISPONIVEL)
    ex2 = Exemplar.objects.create(livro=livro, edicao="1ª Edição", situacao=SituacaoExemplar.DISPONIVEL)
    ex3 = Exemplar.objects.create(livro=livro, edicao="2ª Edição", situacao=SituacaoExemplar.INDISPONIVEL)
    return [ex1, ex2, ex3]
