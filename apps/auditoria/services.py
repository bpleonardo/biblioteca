import logging
from django.db import connection, DatabaseError
from .models import LogSistema

logger = logging.getLogger(__name__)

def registrar_log(id_usuario, descricao):
    """
    Invoca a stored procedure sp_reg_log_sistema no PostgreSQL.
    Caso o banco em uso não possua a procedure ou em caso de fallback,
    registra diretamente no modelo LogSistema.
    """
    if id_usuario is not None:
        try:
            id_usuario = int(id_usuario)
        except (ValueError, TypeError):
            id_usuario = None

    if descricao:
        descricao = str(descricao)[:120]

    try:
        with connection.cursor() as cursor:
            # Chama a stored procedure criada no PostgreSQL
            cursor.execute("CALL sp_reg_log_sistema(%s, %s);", [id_usuario, descricao])
    except DatabaseError as e:
        logger.warning("Falha ao executar stored procedure sp_reg_log_sistema: %s. Utilizando fallback ORM.", e)
        LogSistema.objects.create(id_aluno=id_usuario, descricao=descricao)
