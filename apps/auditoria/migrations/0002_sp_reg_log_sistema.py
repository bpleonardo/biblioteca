from django.db import migrations

CREATE_PROCEDURE_SQL = """
CREATE OR REPLACE PROCEDURE sp_reg_log_sistema(
    p_id_usuario NUMERIC(10, 0),
    p_evento VARCHAR(120)
)
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO tb_log_sistema (id_aluno, descricao, data_registro)
    VALUES (p_id_usuario, p_evento, CURRENT_TIMESTAMP);
END;
$$;
"""

DROP_PROCEDURE_SQL = """
DROP PROCEDURE IF EXISTS sp_reg_log_sistema(NUMERIC(10, 0), VARCHAR(120));
"""

class Migration(migrations.Migration):

    dependencies = [
        ('auditoria', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL(
            sql=CREATE_PROCEDURE_SQL,
            reverse_sql=DROP_PROCEDURE_SQL
        ),
    ]
