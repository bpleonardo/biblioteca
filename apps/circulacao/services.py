from datetime import date
from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils import timezone
from apps.catalogo.models import Exemplar, SituacaoExemplar
from apps.usuarios.models import Usuario
from apps.circulacao.models import Emprestimo, ItemEmprestimo, Reserva, SituacaoReserva
from apps.auditoria.services import registrar_log


def criar_emprestimo(usuario_id, exemplar_ids, data_prevista_devolucao=None, data_emprestimo=None):
    """
    Registra um empréstimo com um ou mais exemplares de forma transacional.
    Garante bloqueio com select_for_update() e validações de negócio.
    """
    if not exemplar_ids:
        raise ValidationError("O empréstimo deve possuir pelo menos um exemplar.")

    # Remover duplicados na mesma operação
    if len(exemplar_ids) != len(set(exemplar_ids)):
        raise ValidationError("Não é permitido incluir exemplares repetidos na mesma operação de empréstimo.")

    hoje = data_emprestimo or date.today()

    if data_prevista_devolucao and data_prevista_devolucao < hoje:
        raise ValidationError("A data prevista de devolução não pode ser anterior à data do empréstimo.")

    with transaction.atomic():
        # Validar usuário
        try:
            usuario = Usuario.objects.get(pk=usuario_id)
        except Usuario.DoesNotExist:
            raise ValidationError("Usuário não encontrado.")

        # Bloquear e buscar exemplares com select_for_update()
        exemplares = list(
            Exemplar.objects.select_for_update()
            .filter(pk__in=exemplar_ids)
        )

        if len(exemplares) != len(exemplar_ids):
            raise ValidationError("Um ou mais exemplares informados não foram encontrados.")

        # Verificar se algum exemplar está indisponível ou já em empréstimo ativo
        for ex in exemplares:
            if ex.situacao != SituacaoExemplar.DISPONIVEL:
                raise ValidationError(f"O exemplar #{ex.id_exemplar} ('{ex.livro.titulo}') não está disponível (situação: {ex.situacao}).")

            # Verificação adicional de empréstimo ativo
            em_aberto = ItemEmprestimo.objects.filter(
                exemplar=ex,
                emprestimo__data_devolucao__isnull=True
            ).exists()
            if em_aberto:
                raise ValidationError(f"O exemplar #{ex.id_exemplar} ('{ex.livro.titulo}') já está em um empréstimo ativo.")

        # Criar cabeçalho do empréstimo
        emprestimo = Emprestimo.objects.create(
            usuario=usuario,
            data_emprestimo=hoje,
            data_prevista_devolucao=data_prevista_devolucao
        )

        # Criar itens e atualizar status dos exemplares
        for ex in exemplares:
            ItemEmprestimo.objects.create(
                emprestimo=emprestimo,
                exemplar=ex
            )
            ex.situacao = SituacaoExemplar.EMPRESTADO
            ex.save(update_fields=['situacao'])

        # Registrar log no sistema
        desc_log = f"Empréstimo #{emprestimo.id_emprestimo} criado para {usuario.nome} com {len(exemplares)} exemplar(es)."
        registrar_log(usuario.id_usuario, desc_log)

        return emprestimo


def devolver_emprestimo(emprestimo_id, data_devolucao=None):
    """
    Realiza a devolução completa de um empréstimo.
    Atualiza todos os exemplares para Disponível e marca data_devolucao.
    """
    hoje = data_devolucao or date.today()

    with transaction.atomic():
        try:
            emprestimo = Emprestimo.objects.select_for_update().get(pk=emprestimo_id)
        except Emprestimo.DoesNotExist:
            raise ValidationError("Empréstimo não encontrado.")

        if emprestimo.data_devolucao is not None:
            raise ValidationError("Este empréstimo já foi devolvido anteriormente.")

        emprestimo.data_devolucao = hoje
        emprestimo.save(update_fields=['data_devolucao'])

        # Atualizar os exemplares para Disponível
        itens = emprestimo.itens.select_related('exemplar').all()
        for item in itens:
            ex = item.exemplar
            ex.situacao = SituacaoExemplar.DISPONIVEL
            ex.save(update_fields=['situacao'])

        desc_log = f"Devolução do Empréstimo #{emprestimo.id_emprestimo} realizada em {hoje:%d/%m/%Y}."
        registrar_log(emprestimo.usuario_id, desc_log)

        return emprestimo


def criar_reserva(usuario_id, livro_id, data_reserva=None):
    """
    Cria uma nova reserva para um livro e usuário.
    """
    hoje = data_reserva or date.today()

    with transaction.atomic():
        try:
            usuario = Usuario.objects.get(pk=usuario_id)
        except Usuario.DoesNotExist:
            raise ValidationError("Usuário não encontrado.")

        reserva = Reserva.objects.create(
            usuario=usuario,
            livro_id=livro_id,
            data_reserva=hoje,
            situacao=SituacaoReserva.PENDENTE
        )

        desc_log = f"Reserva #{reserva.id_reserva} criada para o livro #{livro_id} pelo usuário #{usuario.id_usuario}."
        registrar_log(usuario.id_usuario, desc_log)

        return reserva


def cancelar_reserva(reserva_id):
    """Cancela uma reserva pendente."""
    with transaction.atomic():
        try:
            reserva = Reserva.objects.select_for_update().get(pk=reserva_id)
        except Reserva.DoesNotExist:
            raise ValidationError("Reserva não encontrada.")

        if reserva.situacao != SituacaoReserva.PENDENTE:
            raise ValidationError(f"Não é possível cancelar uma reserva com status '{reserva.situacao}'.")

        reserva.situacao = SituacaoReserva.CANCELADA
        reserva.save(update_fields=['situacao'])

        desc_log = f"Reserva #{reserva.id_reserva} cancelada."
        registrar_log(reserva.usuario_id, desc_log)

        return reserva


def atender_reserva(reserva_id):
    """Marca uma reserva pendente como atendida."""
    with transaction.atomic():
        try:
            reserva = Reserva.objects.select_for_update().get(pk=reserva_id)
        except Reserva.DoesNotExist:
            raise ValidationError("Reserva não encontrada.")

        if reserva.situacao != SituacaoReserva.PENDENTE:
            raise ValidationError(f"Não é possível atender uma reserva com status '{reserva.situacao}'.")

        reserva.situacao = SituacaoReserva.ATENDIDA
        reserva.save(update_fields=['situacao'])

        desc_log = f"Reserva #{reserva.id_reserva} atendida."
        registrar_log(reserva.usuario_id, desc_log)

        return reserva
