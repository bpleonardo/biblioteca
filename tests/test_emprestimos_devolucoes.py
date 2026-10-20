import pytest
from datetime import date, timedelta
from django.core.exceptions import ValidationError
from apps.catalogo.models import SituacaoExemplar
from apps.circulacao.models import Emprestimo, ItemEmprestimo
from apps.circulacao.services import criar_emprestimo, devolver_emprestimo

@pytest.mark.django_db
def test_realizacao_emprestimo_sucesso(usuario, exemplares):
    """Cenário 4: Realização de empréstimo com sucesso."""
    ex1 = exemplares[0]
    ex2 = exemplares[1]
    previsao = date.today() + timedelta(days=7)

    emprestimo = criar_emprestimo(
        usuario_id=usuario.id_usuario,
        exemplar_ids=[ex1.id_exemplar, ex2.id_exemplar],
        data_prevista_devolucao=previsao
    )

    assert emprestimo.id_emprestimo is not None
    assert emprestimo.usuario == usuario
    assert emprestimo.itens.count() == 2
    assert emprestimo.is_ativo is True

    # Verificar que os exemplares foram atualizados para 'Emprestado'
    ex1.refresh_from_db()
    ex2.refresh_from_db()
    assert ex1.situacao == SituacaoExemplar.EMPRESTADO
    assert ex2.situacao == SituacaoExemplar.EMPRESTADO

@pytest.mark.django_db
def test_tentativa_emprestar_exemplar_indisponivel(usuario, exemplares):
    """Cenário 5: Tentativa de emprestar um exemplar indisponível deve falhar."""
    ex_indisp = exemplares[2] # Já criado com SituacaoExemplar.INDISPONIVEL

    with pytest.raises(ValidationError) as exc:
        criar_emprestimo(
            usuario_id=usuario.id_usuario,
            exemplar_ids=[ex_indisp.id_exemplar],
            data_prevista_devolucao=date.today() + timedelta(days=7)
        )
    assert "não está disponível" in str(exc.value)

@pytest.mark.django_db
def test_tentativa_emprestimo_sem_itens(usuario):
    """Cenário 6: Tentativa de empréstimo sem itens deve falhar."""
    with pytest.raises(ValidationError) as exc:
        criar_emprestimo(
            usuario_id=usuario.id_usuario,
            exemplar_ids=[],
            data_prevista_devolucao=date.today() + timedelta(days=7)
        )
    assert "deve possuir pelo menos um exemplar" in str(exc.value)

@pytest.mark.django_db
def test_tentativa_emprestimo_exemplares_duplicados(usuario, exemplares):
    """Não permitir exemplares repetidos na mesma operação."""
    ex1 = exemplares[0]
    with pytest.raises(ValidationError) as exc:
        criar_emprestimo(
            usuario_id=usuario.id_usuario,
            exemplar_ids=[ex1.id_exemplar, ex1.id_exemplar],
            data_prevista_devolucao=date.today() + timedelta(days=7)
        )
    assert "repetidos" in str(exc.value)

@pytest.mark.django_db
def test_devolucao_emprestimo_sucesso(usuario, exemplares):
    """Cenário 7: Devolução de empréstimo."""
    ex1 = exemplares[0]
    emprestimo = criar_emprestimo(
        usuario_id=usuario.id_usuario,
        exemplar_ids=[ex1.id_exemplar],
        data_prevista_devolucao=date.today() + timedelta(days=7)
    )

    devolvido = devolver_emprestimo(emprestimo.id_emprestimo)
    assert devolvido.data_devolucao is not None
    assert devolvido.is_ativo is False

    ex1.refresh_from_db()
    assert ex1.situacao == SituacaoExemplar.DISPONIVEL

@pytest.mark.django_db
def test_tentativa_devolucao_duplicada(usuario, exemplares):
    """Cenário 8: Tentativa de devolução duplicada deve falhar."""
    ex1 = exemplares[0]
    emprestimo = criar_emprestimo(
        usuario_id=usuario.id_usuario,
        exemplar_ids=[ex1.id_exemplar],
        data_prevista_devolucao=date.today() + timedelta(days=7)
    )

    devolver_emprestimo(emprestimo.id_emprestimo)

    with pytest.raises(ValidationError) as exc:
        devolver_emprestimo(emprestimo.id_emprestimo)
    assert "já foi devolvido" in str(exc.value)

@pytest.mark.django_db
def test_identificacao_emprestimos_atrasados(usuario, exemplares):
    """Cenário 10: Identificação de empréstimos atrasados."""
    ex1 = exemplares[0]
    hoje = date.today()

    emp_atrasado = Emprestimo.objects.create(
        usuario=usuario,
        data_emprestimo=hoje - timedelta(days=20),
        data_prevista_devolucao=hoje - timedelta(days=5),
        data_devolucao=None
    )
    ItemEmprestimo.objects.create(emprestimo=emp_atrasado, exemplar=ex1)

    assert emp_atrasado.is_atrasado is True

    # Se devolvido, não é mais atrasado
    emp_atrasado.data_devolucao = hoje
    emp_atrasado.save()
    assert emp_atrasado.is_atrasado is False

@pytest.mark.django_db(transaction=True)
def test_concorrencia_emprestimo_mesmo_exemplar(usuario, exemplares):
    """Cenário 14: Dois empréstimos simultâneos para o mesmo exemplar devem impedir colisão."""
    ex1 = exemplares[0]

    emp1 = criar_emprestimo(
        usuario_id=usuario.id_usuario,
        exemplar_ids=[ex1.id_exemplar],
        data_prevista_devolucao=date.today() + timedelta(days=5)
    )
    assert emp1.id_emprestimo is not None

    # Segunda tentativa imediata com o mesmo exemplar deve falhar
    with pytest.raises(ValidationError) as exc:
        criar_emprestimo(
            usuario_id=usuario.id_usuario,
            exemplar_ids=[ex1.id_exemplar],
            data_prevista_devolucao=date.today() + timedelta(days=5)
        )
    assert "não está disponível" in str(exc.value) or "já está em um empréstimo ativo" in str(exc.value)
