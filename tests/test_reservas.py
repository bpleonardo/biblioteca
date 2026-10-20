import pytest
from django.core.exceptions import ValidationError
from apps.circulacao.models import Reserva, SituacaoReserva
from apps.circulacao.services import criar_reserva, cancelar_reserva, atender_reserva

@pytest.mark.django_db
def test_criacao_e_cancelamento_reserva(usuario, livro):
    """Cenário 9: Criação e cancelamento de reservas."""
    reserva = criar_reserva(usuario_id=usuario.id_usuario, livro_id=livro.id_livro)
    assert reserva.id_reserva is not None
    assert reserva.situacao == SituacaoReserva.PENDENTE

    cancelada = cancelar_reserva(reserva.id_reserva)
    assert cancelada.situacao == SituacaoReserva.CANCELADA

    # Tentativa de cancelar novamente deve falhar
    with pytest.raises(ValidationError):
        cancelar_reserva(reserva.id_reserva)

@pytest.mark.django_db
def test_atendimento_reserva(usuario, livro):
    """Cenário 9: Atendimento de reserva pendente."""
    reserva = criar_reserva(usuario_id=usuario.id_usuario, livro_id=livro.id_livro)
    atendida = atender_reserva(reserva.id_reserva)
    assert atendida.situacao == SituacaoReserva.ATENDIDA

    # Não pode atender reserva já atendida
    with pytest.raises(ValidationError):
        atender_reserva(reserva.id_reserva)
