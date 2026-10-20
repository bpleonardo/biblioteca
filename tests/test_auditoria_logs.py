import pytest
from apps.auditoria.models import LogSistema
from apps.auditoria.services import registrar_log

@pytest.mark.django_db(transaction=True)
def test_registro_log_via_procedure(usuario):
    """Cenário 11: Registro de logs através da stored procedure PostgreSQL."""
    total_antes = LogSistema.objects.count()

    registrar_log(usuario.id_usuario, "Teste de auditoria via stored procedure")

    assert LogSistema.objects.count() == total_antes + 1
    ultimo = LogSistema.objects.latest('id_log')
    assert int(ultimo.id_aluno) == usuario.id_usuario
    assert "Teste de auditoria via stored procedure" in ultimo.descricao
    assert ultimo.data_registro is not None
