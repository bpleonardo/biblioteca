# Sistema de Gerenciamento de Biblioteca

Aplicação web completa para gerenciamento de bibliotecas, desenvolvida com **Django**, **Django REST Framework (DRF)** e **PostgreSQL**, a partir da migração e conversão do esquema de banco de dados relacional original do **Microsoft SQL Server** (`sqlserver.sql`).

O sistema preserva integralmente as **14 tabelas originais**, relacionamentos, nulabilidade, chaves primárias (inclusive chave composta em `tb_livros_autores`), constraints e a stored procedure de log (`sp_reg_log_sistema`).

---

## 1. Tecnologias Utilizadas

| Componente | Tecnologia |
|---|---|
| Linguagem | Python 3.13+ / 3.14 |
| Gerenciador de Pacotes / Ambiente | `uv` com `pyproject.toml` e `uv.lock` |
| Framework Web | Django 6.1+ |
| API REST | Django REST Framework |
| Documentação OpenAPI / Swagger | drf-spectacular (Swagger UI em `/api/docs/`) |
| Banco de Dados | PostgreSQL 16+ |
| Driver de Banco de Dados | `psycopg` (v3) |
| Frontend | Django Templates + Bootstrap 5 + Vanilla JavaScript |
| Testes Automatizados | pytest + pytest-django |
| Containerização | Docker Compose (`compose.yaml`) |

---

## 2. Estrutura Arquitetural do Projeto

A aplicação é monolítica e modularizada em apps com responsabilidades bem definidas:

```text
/
├── config/
│   ├── settings.py          # Configurações globais, banco, auth e DRF
│   ├── urls.py              # Roteamento central (Admin, API, Web, Docs)
│   ├── wsgi.py
│   └── asgi.py
│
├── apps/
│   ├── core/                # Dashboard, views HTML principais e comando seed
│   ├── usuarios/            # Custom User (tb_usuario) e Alunos (tb_aluno)
│   ├── academico/           # Instituições (tb_instituicao) e Cursos (tb_curso)
│   ├── catalogo/            # Editoras, Categorias, Autores, Livros e Exemplares
│   ├── circulacao/          # Empréstimos, Itens e Reservas (regras de negócio)
│   └── auditoria/           # tb_log_sistema e stored procedure sp_reg_log_sistema
│
├── templates/
│   ├── base.html            # Layout base com Bootstrap 5 e navbar
│   ├── dashboard/           # Painel de métricas e eventos recentes
│   ├── catalogo/            # Busca e detalhes de livros com exemplares
│   ├── emprestimos/         # Registro de empréstimo e devolução
│   ├── reservas/            # Gerenciamento de reservas
│   ├── auditoria/           # Consulta paginada aos logs
│   └── usuarios/            # Tela de login
│
├── static/
│   ├── css/custom.css       # Estilização complementar
│   └── js/app.js            # Helpers fetch() com CSRF para a API REST
│
├── database/
│   └── original/
│       └── sqlserver.sql    # Esquema SQL Server original fonte de verdade
│
├── tests/                   # Suite de testes com pytest
├── compose.yaml             # Docker Compose para PostgreSQL
├── pyproject.toml           # Metadados e dependências gerenciadas pelo uv
├── uv.lock                  # Lockfile determinístico
├── .env.example             # Modelo de variáveis de ambiente
└── README.md
```

---

## 3. Mapeamento das 14 Entidades Originais

Todas as 14 tabelas foram preservadas com seus nomes físicos via `db_table`:

| # | Tabela Física | App Django | Responsabilidade | Chave Primária |
|---|---|---|---|---|
| 1 | `tb_editora` | `catalogo` | Editoras de livros | `id_editora` |
| 2 | `tb_categoria` | `catalogo` | Categorias temáticas | `id_categoria` |
| 3 | `tb_instituicao` | `academico` | Instituições de ensino | `id_instituicao` |
| 4 | `tb_curso` | `academico` | Cursos vinculados a instituições | `id_curso` |
| 5 | `tb_usuario` | `usuarios` | Usuários do sistema e autenticação | `id_usuario` |
| 6 | `tb_aluno` | `usuarios` | Alunos (vínculo com usuário e curso) | `id_aluno` |
| 7 | `tb_autores` | `catalogo` | Autores de obras | `id_autor` |
| 8 | `tb_livros` | `catalogo` | Obras bibliográficas | `id_livro` |
| 9 | `tb_livros_autores`| `catalogo` | Associação N:N entre livros e autores | **Chave Composta** (`id_livro`, `id_autor`) |
| 10 | `tb_exemplares` | `catalogo` | Exemplares físicos de cada livro | `id_exemplar` |
| 11 | `tb_reserva` | `circulacao` | Reservas de livros por usuários | `id_reserva` |
| 12 | `tb_emprestimo` | `circulacao` | Empréstimos de livros | `id_emprestimo` |
| 13 | `tb_item_emprestimo` | `circulacao` | Exemplares associados ao empréstimo | `id_item_emprestimo` |
| 14 | `tb_log_sistema` | `auditoria` | Registros de logs e auditoria | `id_log` |

---

## 4. Diferenças entre SQL Server e PostgreSQL & Decisões de Modelagem

1. **Tipos de Dados e Dialetos:**
   - `IDENTITY(1,1)` do SQL Server convertido para identidades/sequences no PostgreSQL (`AutoField`).
   - `DATETIME` convertido para `TIMESTAMP WITH TIME ZONE`.
   - `DECIMAL(10, 0)` convertido para `NUMERIC(10, 0)`.
   - `DEFAULT CAST(GETDATE() AS DATE)` e `GETDATE()` convertidos para valores padrão do Django e PostgreSQL (`CURRENT_DATE`, `CURRENT_TIMESTAMP`).

2. **Chave Primária Composta em `tb_livros_autores`:**
   - O SQL Server original definia `PRIMARY KEY (id_livro, id_autor)`.
   - O projeto utilizou o recurso nativo de chave primária composta do Django (`models.CompositePrimaryKey('livro', 'autor')`), preservando exatamente a estrutura física original com apenas duas colunas (`id_livro` e `id_autor`), **sem adicionar artificialmente uma coluna `id`**.

3. **Autenticação em `tb_usuario`:**
   - O modelo `Usuario` herda de `AbstractBaseUser` e implementa `BaseUserManager`.
   - As únicas colunas físicas na tabela são: `id_usuario`, `nome`, `email` e `senha` (`db_column='senha'`).
   - O atributo padrão `last_login` do Django foi suprimido no modelo para não criar colunas adicionais no banco.
   - Permissões do Django Admin (`is_staff`, `is_active`, `is_superuser`, `has_perm`) foram implementadas como propriedades/métodos em nível de classe Python, sem poluir a tabela física original.
   - Senhas são armazenadas exclusivamente utilizando hashes seguros (PBKDF2/SHA256).

4. **Stored Procedure `sp_reg_log_sistema`:**
   - Criada no PostgreSQL por meio de Django Migrations (`RunSQL`).
   - Preservada a particularidade original: o parâmetro `@p_id_usuario` é gravado na coluna física `id_aluno` de `tb_log_sistema`.
   - Invocada via serviço Python (`apps.auditoria.services.registrar_log`) através de `CALL sp_reg_log_sistema(%s, %s);`.

5. **Regras de Negócio na Circulação:**
   - Operações de empréstimo executadas sob `transaction.atomic()` com `select_for_update()` sobre os exemplares selecionados para prevenção de concorrência e condições de corrida.
   - Validação de disponibilidade do exemplar, integridade de datas e proibição de itens repetidos.
   - Devolução atômica abrangendo todos os exemplares vinculados ao cabeçalho do empréstimo (`tb_emprestimo`), conforme modelagem original.

---

## 5. Pré-requisitos e Instalação

### Requisitos
- **Python 3.13+** (ou Python 3.14)
- **uv** (gerenciador de dependências rápido da Astral): `curl -LsSf https://astral.sh/uv/install.sh | sh`
- **PostgreSQL 16+** (localmente ou via Docker Compose)

---

## 6. Passo a Passo para Execução

### 1. Clonar e Acessar o Repositório
```bash
git clone https://github.com/bpleonardo/biblioteca
cd biblioteca
```

### 2. Configurar o Ambiente (.env)
Copie o arquivo de exemplo:
```bash
cp .env.example .env
```
Edite as variáveis no `.env` se necessário:
```ini
DEBUG=True
SECRET_KEY=sua-chave-secreta
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

DB_NAME=biblioteca
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432
```

### 3. Iniciar o Banco PostgreSQL
Caso deseje rodar o PostgreSQL via Docker:
```bash
docker compose up -d postgres
```
*(Se você já possui o PostgreSQL rodando localmente na porta 5432 com as credenciais acima, pode pular esta etapa).*

### 4. Instalar Dependências com o uv
```bash
uv sync
```

### 5. Executar as Migrations
Cria as 14 tabelas, relacionamentos, constraints e a stored procedure no PostgreSQL:
```bash
uv run python manage.py migrate
```

### 6. Carregar Dados de Demonstração (Seed)
Popula o banco com dados realistas, múltiplos autores, exemplares, empréstimos (ativos, concluídos e atrasados), reservas e logs:
```bash
uv run python manage.py seed
```

### 7. Iniciar o Servidor de Desenvolvimento
```bash
uv run python manage.py runserver
```
A aplicação estará disponível em `http://127.0.0.1:8000/`.

---

## 7. Acesso às Interfaces e Controle de Acesso

- **Página Inicial / Dashboard:** [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
  - *Visitantes não autenticados:* Visualizam exclusivamente os indicadores públicos (Total de Títulos e Exemplares Disponíveis).
  - *Usuários autenticados:* Visualizam o Dashboard completo (indicadores de circulação, atrasos, reservas e histórico de movimentações).
- **Catálogo Público de Livros:** [http://127.0.0.1:8000/catalogo/](http://127.0.0.1:8000/catalogo/)
  - Consulta pública com busca por título, filtros e cálculo em tempo real de exemplares disponíveis.
  - Ações de empréstimo convidam visitantes a entrar no sistema ("Entrar para solicitar empréstimo").
- **Empréstimos e Devoluções (Restrito):** [http://127.0.0.1:8000/emprestimos/](http://127.0.0.1:8000/emprestimos/)
- **Gerenciamento de Reservas (Restrito):** [http://127.0.0.1:8000/reservas/](http://127.0.0.1:8000/reservas/)
- **Auditoria de Logs (Restrito):** [http://127.0.0.1:8000/logs/](http://127.0.0.1:8000/logs/)
- **Django Admin:** [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)
- **Documentação Interativa da API (Swagger UI):** [http://127.0.0.1:8000/api/docs/](http://127.0.0.1:8000/api/docs/)
- **Esquema OpenAPI:** [http://127.0.0.1:8000/api/schema/](http://127.0.0.1:8000/api/schema/)

### Credenciais Padrão (Criadas pelo Seed)
- *Administrador:**
  - E-mail: `admin@biblioteca.local`
  - Senha: `senha123`
- **Alunos / Leitores:**
  - `ana.silva@email.com` / `senha123`
  - `carlos.oliveira@email.com` / `senha123`
  - `beatriz.santos@email.com` / `senha123`
  - `lucas.pereira@email.com` / `senha123`

---

## 8. Execução dos Testes Automatizados

A suíte de testes cobre integralmente as regras de negócio, concorrência, integridade referencial e endpoints da API, executando contra o PostgreSQL:

```bash
uv run pytest -v
```

### Cenários Cobertos:
1. `test_criacao_usuario_e_aluno`: Cadastro de usuários e alunos com senhas criptografadas.
2. `test_cadastro_livro_com_multiplos_autores`: Relação N:N preservando chave primária composta.
3. `test_cadastro_exemplares`: Cadastro de exemplares com situações controladas.
4. `test_realizacao_emprestimo_sucesso`: Empréstimo atômico atualizando status para 'Emprestado'.
5. `test_tentativa_emprestar_exemplar_indisponivel`: Bloqueio de exemplar indisponível.
6. `test_tentativa_emprestimo_sem_itens`: Bloqueio de empréstimo sem exemplares.
7. `test_devolucao_emprestimo_sucesso`: Devolução atômica retornando exemplares para 'Disponível'.
8. `test_tentativa_devolucao_duplicada`: Impedimento de devoluções repetidas.
9. `test_criacao_e_cancelamento_reserva` & `test_atendimento_reserva`: Ciclo de vida das reservas.
10. `test_identificacao_emprestimos_atrasados`: Detecção precisa de atrasos por data prevista.
11. `test_registro_log_via_procedure`: Invocação da stored procedure `sp_reg_log_sistema` no PostgreSQL.
12. `test_api_login_e_me`: Autenticação e segurança contra vazamento de hashes de senha.
13. `test_integridade_referencial_usuario_aluno` & `test_integridade_referencial_curso_protegido`: Constraints `CASCADE` e `PROTECT`.
14. `test_concorrencia_emprestimo_mesmo_exemplar`: Bloqueio com `select_for_update()` contra concorrência simultânea.
