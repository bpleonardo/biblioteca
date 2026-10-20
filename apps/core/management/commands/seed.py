from datetime import date, timedelta
from django.core.management.base import BaseCommand
from django.db import transaction
from django.contrib.auth.hashers import make_password

from apps.usuarios.models import Usuario, Aluno
from apps.academico.models import Instituicao, Curso
from apps.catalogo.models import (
    Editora, Categoria, Autor, Livro, LivroAutor, Exemplar, SituacaoExemplar
)
from apps.circulacao.models import Emprestimo, ItemEmprestimo, Reserva, SituacaoReserva
from apps.auditoria.models import LogSistema
from apps.auditoria.services import registrar_log

class Command(BaseCommand):
    help = "Popula o banco de dados com dados de demonstração completos, reproduzíveis e seguros."

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Iniciando a carga de dados de demonstração (seed)..."))

        with transaction.atomic():
            # 1. Instituições
            inst_usp, _ = Instituicao.objects.get_or_create(
                nome="Universidade de São Paulo (USP)"
            )
            inst_unicamp, _ = Instituicao.objects.get_or_create(
                nome="Universidade Estadual de Campinas (UNICAMP)"
            )
            inst_ufmg, _ = Instituicao.objects.get_or_create(
                nome="Universidade Federal de Minas Gerais (UFMG)"
            )

            # 2. Cursos
            curso_cc, _ = Curso.objects.get_or_create(
                nome="Ciência da Computação",
                instituicao=inst_usp
            )
            curso_si, _ = Curso.objects.get_or_create(
                nome="Sistemas de Informação",
                instituicao=inst_usp
            )
            curso_eng, _ = Curso.objects.get_or_create(
                nome="Engenharia de Software",
                instituicao=inst_unicamp
            )
            curso_mat, _ = Curso.objects.get_or_create(
                nome="Matemática Aplicada",
                instituicao=inst_ufmg
            )

            # 3. Usuários (com senhas devidamente criptografadas)
            senha_padrao = "senha123"
            hash_senha = make_password(senha_padrao)

            admin_user, _ = Usuario.objects.get_or_create(
                email="admin@biblioteca.local",
                defaults={"nome": "Administrador do Sistema", "password": hash_senha}
            )
            if not admin_user.password.startswith("pbkdf2_") and not admin_user.password.startswith("argon2"):
                admin_user.set_password(senha_padrao)
                admin_user.save()

            u_ana, _ = Usuario.objects.get_or_create(
                email="ana.silva@email.com",
                defaults={"nome": "Ana Clara Silva", "password": hash_senha}
            )
            u_carlos, _ = Usuario.objects.get_or_create(
                email="carlos.oliveira@email.com",
                defaults={"nome": "Carlos Eduardo Oliveira", "password": hash_senha}
            )
            u_beatriz, _ = Usuario.objects.get_or_create(
                email="beatriz.santos@email.com",
                defaults={"nome": "Beatriz Lima Santos", "password": hash_senha}
            )
            u_lucas, _ = Usuario.objects.get_or_create(
                email="lucas.pereira@email.com",
                defaults={"nome": "Lucas Martins Pereira", "password": hash_senha}
            )

            # 4. Alunos vinculados a usuários e cursos
            Aluno.objects.get_or_create(
                usuario=u_ana,
                curso=curso_cc,
                defaults={"matricula": "2024-CC-001"}
            )
            Aluno.objects.get_or_create(
                usuario=u_carlos,
                curso=curso_si,
                defaults={"matricula": "2024-SI-002"}
            )
            Aluno.objects.get_or_create(
                usuario=u_beatriz,
                curso=curso_eng,
                defaults={"matricula": "2024-ES-003"}
            )
            Aluno.objects.get_or_create(
                usuario=u_lucas,
                curso=curso_mat,
                defaults={"matricula": "2024-MA-004"}
            )

            # 5. Editoras
            ed_novatec, _ = Editora.objects.get_or_create(
                nome="Novatec Editora",
                defaults={"cnpj": "04.567.890/0001-12"}
            )
            ed_oreilly, _ = Editora.objects.get_or_create(
                nome="O'Reilly Media",
                defaults={"cnpj": "12.345.678/0001-99"}
            )
            ed_campus, _ = Editora.objects.get_or_create(
                nome="Campus Elsevier",
                defaults={"cnpj": "98.765.432/0001-55"}
            )
            ed_companhia, _ = Editora.objects.get_or_create(
                nome="Companhia das Letras",
                defaults={"cnpj": "55.443.221/0001-00"}
            )

            # 6. Categorias
            cat_prog, _ = Categoria.objects.get_or_create(descricao="Programação e Algoritmos")
            cat_bd, _ = Categoria.objects.get_or_create(descricao="Bancos de Dados e Modelagem")
            cat_es, _ = Categoria.objects.get_or_create(descricao="Engenharia de Software e Padrões")
            cat_redes, _ = Categoria.objects.get_or_create(descricao="Redes e Infraestrutura")

            # 7. Autores
            aut_martin, _ = Autor.objects.get_or_create(
                nome="Robert C. Martin",
                defaults={"email": "unclebob@cleancoder.com", "editora": ed_campus}
            )
            aut_fowler, _ = Autor.objects.get_or_create(
                nome="Martin Fowler",
                defaults={"email": "fowler@thoughtworks.com", "editora": ed_oreilly}
            )
            aut_gamma, _ = Autor.objects.get_or_create(
                nome="Erich Gamma",
                defaults={"email": "egamma@gangoffour.org", "editora": ed_campus}
            )
            aut_helm, _ = Autor.objects.get_or_create(
                nome="Richard Helm",
                defaults={"email": "rhelm@gangoffour.org", "editora": ed_campus}
            )
            aut_date, _ = Autor.objects.get_or_create(
                nome="C. J. Date",
                defaults={"email": "cjdate@database.org", "editora": ed_novatec}
            )
            aut_navathe, _ = Autor.objects.get_or_create(
                nome="Shamkant B. Navathe",
                defaults={"email": "navathe@gatech.edu", "editora": ed_novatec}
            )
            aut_elmasri, _ = Autor.objects.get_or_create(
                nome="Ramez Elmasri",
                defaults={"email": "elmasri@uta.edu", "editora": ed_novatec}
            )

            # 8. Livros com Múltiplos Autores
            # Livro 1: Design Patterns (GoF - múltiplos autores)
            livro_gof, _ = Livro.objects.get_or_create(
                titulo="Padrões de Projeto: Soluções Reutilizáveis de Software Orientado a Objetos",
                defaults={
                    "isbn": "978-8573076103",
                    "categoria": cat_es,
                    "editora": ed_campus
                }
            )
            livro_gof.autores.set([aut_gamma, aut_helm])

            # Livro 2: Sistemas de Banco de Dados (Elmasri & Navathe - múltiplos autores)
            livro_bd, _ = Livro.objects.get_or_create(
                titulo="Sistemas de Banco de Dados",
                defaults={
                    "isbn": "978-8580550312",
                    "categoria": cat_bd,
                    "editora": ed_novatec
                }
            )
            livro_bd.autores.set([aut_elmasri, aut_navathe, aut_date])

            # Livro 3: Clean Code (Robert Martin)
            livro_clean, _ = Livro.objects.get_or_create(
                titulo="Código Limpo: Habilidades Práticas do Agile Software",
                defaults={
                    "isbn": "978-8576082675",
                    "categoria": cat_prog,
                    "editora": ed_campus
                }
            )
            livro_clean.autores.set([aut_martin])

            # Livro 4: Refatoração (Martin Fowler)
            livro_refact, _ = Livro.objects.get_or_create(
                titulo="Refatoração: Aperfeiçoando o Design de Código Existente",
                defaults={
                    "isbn": "978-8575227244",
                    "categoria": cat_prog,
                    "editora": ed_novatec
                }
            )
            livro_refact.autores.set([aut_fowler])

            # 9. Exemplares físicos dos livros
            # Para Livro GoF: 3 exemplares
            ex_gof_1, _ = Exemplar.objects.get_or_create(livro=livro_gof, edicao="1ª Edição", defaults={"situacao": SituacaoExemplar.DISPONIVEL})
            ex_gof_2, _ = Exemplar.objects.get_or_create(livro=livro_gof, edicao="1ª Edição (Rev.)", defaults={"situacao": SituacaoExemplar.DISPONIVEL})
            ex_gof_3, _ = Exemplar.objects.get_or_create(livro=livro_gof, edicao="2ª Edição", defaults={"situacao": SituacaoExemplar.DISPONIVEL})

            # Para Livro BD: 3 exemplares
            ex_bd_1, _ = Exemplar.objects.get_or_create(livro=livro_bd, edicao="6ª Edição", defaults={"situacao": SituacaoExemplar.DISPONIVEL})
            ex_bd_2, _ = Exemplar.objects.get_or_create(livro=livro_bd, edicao="6ª Edição", defaults={"situacao": SituacaoExemplar.DISPONIVEL})
            ex_bd_3, _ = Exemplar.objects.get_or_create(livro=livro_bd, edicao="7ª Edição", defaults={"situacao": SituacaoExemplar.DISPONIVEL})

            # Para Livro Clean Code: 2 exemplares
            ex_clean_1, _ = Exemplar.objects.get_or_create(livro=livro_clean, edicao="1ª Edição", defaults={"situacao": SituacaoExemplar.DISPONIVEL})
            ex_clean_2, _ = Exemplar.objects.get_or_create(livro=livro_clean, edicao="1ª Edição Especial", defaults={"situacao": SituacaoExemplar.DISPONIVEL})

            # Para Livro Refatoração: 2 exemplares
            ex_ref_1, _ = Exemplar.objects.get_or_create(livro=livro_refact, edicao="2ª Edição", defaults={"situacao": SituacaoExemplar.DISPONIVEL})
            ex_ref_2, _ = Exemplar.objects.get_or_create(livro=livro_refact, edicao="2ª Edição", defaults={"situacao": SituacaoExemplar.DISPONIVEL})

            hoje = date.today()

            # 10. Empréstimos: Ativo, Concluído e Atrasado
            # A) Empréstimo Concluído (devolvido)
            emp_concluido, _ = Emprestimo.objects.get_or_create(
                usuario=u_ana,
                data_emprestimo=hoje - timedelta(days=20),
                defaults={
                    "data_prevista_devolucao": hoje - timedelta(days=6),
                    "data_devolucao": hoje - timedelta(days=7)
                }
            )
            ItemEmprestimo.objects.get_or_create(emprestimo=emp_concluido, exemplar=ex_gof_1)
            ex_gof_1.situacao = SituacaoExemplar.DISPONIVEL
            ex_gof_1.save(update_fields=['situacao'])

            # B) Empréstimo Ativo (dentro do prazo)
            emp_ativo, _ = Emprestimo.objects.get_or_create(
                usuario=u_carlos,
                data_emprestimo=hoje - timedelta(days=3),
                defaults={
                    "data_prevista_devolucao": hoje + timedelta(days=11),
                    "data_devolucao": None
                }
            )
            ItemEmprestimo.objects.get_or_create(emprestimo=emp_ativo, exemplar=ex_bd_1)
            ex_bd_1.situacao = SituacaoExemplar.EMPRESTADO
            ex_bd_1.save(update_fields=['situacao'])

            # C) Empréstimo Atrasado (data_prevista_devolucao anterior a hoje, sem devolucao)
            emp_atrasado, _ = Emprestimo.objects.get_or_create(
                usuario=u_beatriz,
                data_emprestimo=hoje - timedelta(days=25),
                defaults={
                    "data_prevista_devolucao": hoje - timedelta(days=5),
                    "data_devolucao": None
                }
            )
            ItemEmprestimo.objects.get_or_create(emprestimo=emp_atrasado, exemplar=ex_clean_1)
            ex_clean_1.situacao = SituacaoExemplar.EMPRESTADO
            ex_clean_1.save(update_fields=['situacao'])

            # 11. Reservas: Pendentes e Concluídas/Canceladas
            Reserva.objects.get_or_create(
                usuario=u_lucas,
                livro=livro_clean,
                defaults={
                    "data_reserva": hoje - timedelta(days=2),
                    "situacao": SituacaoReserva.PENDENTE
                }
            )
            Reserva.objects.get_or_create(
                usuario=u_ana,
                livro=livro_bd,
                defaults={
                    "data_reserva": hoje - timedelta(days=1),
                    "situacao": SituacaoReserva.PENDENTE
                }
            )
            Reserva.objects.get_or_create(
                usuario=u_carlos,
                livro=livro_gof,
                defaults={
                    "data_reserva": hoje - timedelta(days=15),
                    "situacao": SituacaoReserva.ATENDIDA
                }
            )
            Reserva.objects.get_or_create(
                usuario=u_beatriz,
                livro=livro_refact,
                defaults={
                    "data_reserva": hoje - timedelta(days=10),
                    "situacao": SituacaoReserva.CANCELADA
                }
            )

            # 12. Registros de Log via Stored Procedure
            registrar_log(admin_user.id_usuario, "Inicialização do sistema e carga inicial de parâmetros.")
            registrar_log(u_ana.id_usuario, f"Empréstimo #{emp_concluido.id_emprestimo} devolvido com sucesso.")
            registrar_log(u_carlos.id_usuario, f"Empréstimo #{emp_ativo.id_emprestimo} registrado para Carlos Eduardo.")
            registrar_log(u_beatriz.id_usuario, f"Notificação de atraso emitida para Empréstimo #{emp_atrasado.id_emprestimo}.")
            registrar_log(u_lucas.id_usuario, "Reserva registrada para o livro 'Código Limpo'.")

        self.stdout.write(self.style.SUCCESS("✓ Dados de demonstração carregados com sucesso!"))
        self.stdout.write(self.style.SUCCESS("  - Usuário administrador: admin@biblioteca.local (senha: senha123)"))
        self.stdout.write(self.style.SUCCESS("  - Usuários alunos: ana.silva@email.com, carlos.oliveira@email.com, etc. (senha: senha123)"))
