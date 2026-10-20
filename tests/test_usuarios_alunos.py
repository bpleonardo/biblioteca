import pytest
from django.db.models.deletion import ProtectedError
from apps.usuarios.models import Usuario, Aluno

@pytest.mark.django_db
def test_criacao_usuario_e_aluno(usuario, aluno):
    """Cenário 1: Criação de usuários e alunos com senhas em hash."""
    assert usuario.id_usuario is not None
    assert usuario.email == "leitor@teste.com"
    assert usuario.check_password("segredo_teste") is True
    assert not usuario.password.startswith("segredo_teste")
    assert aluno.id_aluno is not None
    assert aluno.usuario == usuario
    assert aluno.matricula == "TEST-2024-001"

@pytest.mark.django_db
def test_integridade_referencial_usuario_aluno(usuario, aluno):
    """Cenário 13: Deleção do usuário deve cascatear para o aluno."""
    usuario_id = usuario.id_usuario
    aluno_id = aluno.id_aluno

    usuario.delete()

    assert not Usuario.objects.filter(pk=usuario_id).exists()
    assert not Aluno.objects.filter(pk=aluno_id).exists()

@pytest.mark.django_db
def test_integridade_referencial_curso_protegido(aluno, curso):
    """Cenário 13: Tentativa de deletar curso associado a aluno deve falhar (ON DELETE NO ACTION / PROTECT)."""
    with pytest.raises(ProtectedError):
        curso.delete()
