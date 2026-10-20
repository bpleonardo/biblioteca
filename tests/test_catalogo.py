import pytest

from apps.catalogo.models import Livro, Exemplar, LivroAutor, SituacaoExemplar


@pytest.mark.django_db
def test_cadastro_livro_com_multiplos_autores(livro, autores):
    """Cenário 2: Cadastro de livros com múltiplos autores."""
    assert livro.id_livro is not None
    assert livro.autores.count() == 2
    for autor in autores:
        assert autor in livro.autores.all()

    # Verificar que tb_livros_autores registra o relacionamento corretamente
    associacoes = LivroAutor.objects.filter(livro=livro)
    assert associacoes.count() == 2


@pytest.mark.django_db
def test_cadastro_exemplares(livro, exemplares):
    """Cenário 3: Cadastro de exemplares com situações consistentes."""
    assert len(exemplares) == 3
    assert Exemplar.objects.filter(livro=livro).count() == 3

    disp = Exemplar.objects.filter(
        livro=livro, situacao=SituacaoExemplar.DISPONIVEL
    ).count()
    assert disp == 2

    indisp = Exemplar.objects.filter(
        livro=livro, situacao=SituacaoExemplar.INDISPONIVEL
    ).count()
    assert indisp == 1
