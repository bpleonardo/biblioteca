# Especificação — Sistema de Gerenciamento de Biblioteca

## 1. Objetivo

Desenvolver uma aplicação web completa para gerenciamento de bibliotecas, utilizando Django e PostgreSQL, a partir do esquema de banco de dados disponibilizado no arquivo `sqlserver.sql`.

O esquema original foi desenvolvido para Microsoft SQL Server. A aplicação deverá convertê-lo para PostgreSQL, preservando integralmente sua estrutura lógica, entidades, relacionamentos e restrições.

O sistema deverá contemplar:

- Gerenciamento de usuários e alunos.
- Cadastro e consulta de livros.
- Gerenciamento de autores, editoras e categorias.
- Controle de exemplares físicos.
- Registro de empréstimos e devoluções.
- Gerenciamento de reservas.
- Cadastro de instituições e cursos.
- Registro e consulta de logs.
- API REST funcional.
- Frontend administrativo integrado.

O objetivo é entregar uma aplicação acadêmica completa, funcional e organizada, sem introduzir complexidade arquitetural desnecessária.

## 2. Stack tecnológica

### Tecnologias obrigatórias

| Componente | Tecnologia |
|---|---|
| Linguagem | Python 3.13+ |
| Gerenciador Python | uv (astral-sh/uv) |
| Framework | Django |
| API REST | Django REST Framework |
| Banco de dados | PostgreSQL |
| ORM | Django ORM |
| Migrações | Django Migrations |
| Frontend | Django Templates |
| CSS | Bootstrap 5 |
| JavaScript | Vanilla JavaScript |
| Testes | pytest + pytest-django |
| Infraestrutura | Docker Compose |

Utilizar versões estáveis e compatíveis das dependências.

O projeto deverá utilizar `pyproject.toml` e `uv.lock`, evitando o uso de `requirements.txt` como mecanismo principal de gerenciamento de dependências.

### Decisões arquiteturais

A aplicação deverá ser monolítica.

Não criar um projeto frontend separado com React, Next.js, Vue ou outro framework JavaScript.

O próprio Django deverá disponibilizar:

1. API REST.
2. Páginas HTML.
3. Arquivos estáticos.
4. Autenticação.
5. Django Admin.
6. Acesso ao banco de dados.

O frontend deverá consumir a API REST para suas operações de negócio, mantendo uma separação clara entre apresentação e regras de negócio.

Não utilizar FastAPI, SQLAlchemy ou Alembic.

---

## 3. Análise e migração do banco original

O arquivo `sqlserver.sql` deverá ser considerado a fonte de verdade da modelagem inicial.

Antes de iniciar a implementação, analisar todas as tabelas, colunas, constraints, relacionamentos e a stored procedure existente.

### 3.1 Entidades obrigatórias

O esquema contém 14 tabelas:

| Tabela | Responsabilidade |
|---|---|
| `tb_editora` | Editoras |
| `tb_categoria` | Categorias dos livros |
| `tb_instituicao` | Instituições de ensino |
| `tb_curso` | Cursos |
| `tb_usuario` | Usuários |
| `tb_aluno` | Dados acadêmicos |
| `tb_autores` | Autores |
| `tb_livros` | Obras bibliográficas |
| `tb_livros_autores` | Relacionamento N:N entre livros e autores |
| `tb_exemplares` | Exemplares físicos |
| `tb_reserva` | Reservas |
| `tb_emprestimo` | Empréstimos |
| `tb_item_emprestimo` | Itens dos empréstimos |
| `tb_log_sistema` | Logs de eventos |

Todas deverão possuir modelos Django correspondentes e utilização efetiva na aplicação.

### 3.2 Preservação da estrutura

Utilizar `Meta.db_table` para preservar os nomes originais das tabelas.

Preservar também:

- Nomes das colunas.
- Chaves primárias.
- Chaves estrangeiras.
- Nulabilidade.
- Tamanhos dos campos.
- Restrições de unicidade.
- Valores padrão.
- Comportamentos de exclusão.
- Relacionamentos.

Utilizar `db_column` quando necessário.

Não adicionar automaticamente um campo `id` aos modelos que já possuem identificadores próprios.

**Atenção especial à tabela `tb_livros_autores`:** o esquema original possui chave primária composta por `id_livro` e `id_autor`.

Utilizar os recursos de chave primária composta do Django, caso suportados pela versão escolhida, ou apresentar uma solução compatível que preserve a estrutura física original. Não adicionar uma coluna identificadora artificial silenciosamente.

### 3.3 Conversão SQL Server → PostgreSQL

Realizar as conversões necessárias:

- `IDENTITY` para identidade PostgreSQL.
- `GETDATE()` para `CURRENT_TIMESTAMP`.
- `CAST(GETDATE() AS DATE)` para `CURRENT_DATE`.
- `DATETIME` para `TIMESTAMP`.
- `DECIMAL(10,0)` para `NUMERIC(10,0)`.
- Remoção de `GO` e `USE`.
- Conversão da sintaxe da stored procedure.

Utilizar Django Migrations para criar e gerenciar o esquema.

Não utilizar `migrate --fake` como solução para incompatibilidades.

Não depender da execução manual do SQL Server original.

### 3.4 Stored procedure

O arquivo original contém:

`sp_reg_log_sistema`

Sua responsabilidade é inserir registros em `tb_log_sistema`.

Implementar comportamento equivalente no PostgreSQL por meio de uma função ou procedure, criada através de uma migration Django com `RunSQL`.

Disponibilizar também um serviço Python responsável por invocar essa funcionalidade.

Preservar a particularidade original: o parâmetro da procedure é denominado `p_id_usuario`, mas seu valor é armazenado na coluna `id_aluno`.

Não inventar uma chave estrangeira para essa coluna.

---

## 4. Organização do projeto

Sugestão de estrutura:

```text
/
├── config/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
├── apps/
│   ├── core/
│   ├── usuarios/
│   ├── academico/
│   ├── catalogo/
│   ├── circulacao/
│   └── auditoria/
│
├── templates/
│   ├── base.html
│   ├── dashboard/
│   ├── catalogo/
│   ├── usuarios/
│   ├── emprestimos/
│   └── reservas/
│
├── static/
│   ├── css/
│   └── js/
│
├── database/
│   ├── original/
│   │   └── sqlserver.sql
│   └── seeds/
│
├── manage.py
├── pyproject.toml
├── uv.lock
├── compose.yaml
├── .env.example
└── README.md
```

### Responsabilidade dos apps

**core:** funcionalidades compartilhadas, dashboard e infraestrutura comum.

**usuarios:** usuários, alunos e autenticação.

**academico:** instituições e cursos.

**catalogo:** editoras, categorias, autores, livros e exemplares.

**circulacao:** reservas, empréstimos, itens e devoluções.

**auditoria:** logs e integração com a rotina PostgreSQL.

A organização poderá ser adaptada quando houver justificativa técnica.

Evitar criar um app Django para cada tabela individualmente.

---

## 5. Autenticação e usuários

O esquema original possui a tabela `tb_usuario`, contendo:

- `id_usuario`
- `nome`
- `email`
- `senha`

Essa estrutura deverá ser preservada.

Implementar autenticação utilizando os mecanismos de hash de senha e gerenciamento de sessão do Django.

Preferencialmente, implementar um modelo de usuário personalizado com `AbstractBaseUser` e `BaseUserManager`, utilizando `tb_usuario` como tabela física.

Configurar `AUTH_USER_MODEL` antes da criação das migrações iniciais.

O e-mail deverá funcionar como identificador de autenticação.

Não criar uma segunda tabela de usuários que duplique desnecessariamente os dados existentes.

Campos adicionais exigidos por interfaces ou permissões internas do Django deverão ser avaliados cuidadosamente e documentados, sem alterar arbitrariamente o esquema original.

Caso o Django Admin exija uma estrutura adicional de permissões, utilizar uma solução compatível com o modelo original.

As senhas deverão ser armazenadas exclusivamente utilizando hashes seguros.

Implementar:

- Login.
- Logout.
- Proteção das páginas administrativas.
- Proteção dos endpoints que exigem autenticação.
- Controle básico de acesso.

Não é necessário implementar um sistema complexo de papéis e permissões.

---

## 6. Django Admin

Utilizar o Django Admin para facilitar o gerenciamento das entidades cadastrais.

Registrar os modelos apropriados e configurar:

- `list_display`
- `search_fields`
- `list_filter`
- `ordering`
- `autocomplete_fields`, quando aplicável.
- Formulários com validação.

Priorizar o Django Admin para:

- Editoras.
- Categorias.
- Autores.
- Instituições.
- Cursos.
- Usuários.
- Alunos.

Permitir também consultar livros e exemplares.

Entretanto, **o Django Admin não deverá substituir toda a aplicação**.

Os fluxos principais de gerenciamento da biblioteca deverão possuir páginas próprias, adequadas às operações realizadas pelos usuários.

Não permitir que operações genéricas do Admin contornem regras de integridade, especialmente empréstimos e devoluções.

---

## 7. Funcionalidades obrigatórias

### 7.1 Cadastro acadêmico

Implementar gerenciamento de instituições, cursos e alunos.

Permitir:

- Cadastrar instituições.
- Associar cursos a instituições.
- Associar alunos a usuários existentes.
- Vincular alunos a cursos.
- Consultar os dados acadêmicos de cada aluno.
- Pesquisar alunos por nome, e-mail ou matrícula.

Respeitar os relacionamentos e comportamentos de exclusão existentes no SQL original.

### 7.2 Catálogo de livros

Implementar uma interface própria para consulta e gerenciamento do catálogo.

Funcionalidades:

- Cadastrar livros.
- Editar dados bibliográficos.
- Associar editoras e categorias.
- Associar múltiplos autores.
- Pesquisar por título, ISBN, autor, editora ou categoria.
- Consultar os exemplares de cada obra.
- Visualizar a disponibilidade dos exemplares.

Utilizar o relacionamento N:N original através de `tb_livros_autores`.

Não substituir a associação por campos textuais.

### 7.3 Exemplares

Um livro poderá possuir múltiplos exemplares físicos.

Cada exemplar deverá utilizar os campos originais:

- `id_exemplar`
- `id_livro`
- `edicao`
- `situacao`

Definir valores consistentes para `situacao`, por exemplo:

- Disponível.
- Emprestado.
- Indisponível.

Centralizar os valores permitidos em `TextChoices` ou estrutura equivalente.

A situação deverá permanecer sincronizada com as operações de empréstimo e devolução.

### 7.4 Empréstimos

Implementar uma interface própria para registrar empréstimos.

Fluxo esperado:

1. Selecionar o usuário.
2. Pesquisar exemplares disponíveis.
3. Adicionar um ou mais exemplares ao empréstimo.
4. Definir a data prevista de devolução.
5. Confirmar a operação.
6. Apresentar o resumo do empréstimo realizado.

Utilizar `tb_emprestimo` e `tb_item_emprestimo`.

Regras obrigatórias:

- Um empréstimo deverá possuir pelo menos um exemplar.
- Um exemplar não poderá participar de dois empréstimos ativos simultaneamente.
- Não permitir exemplares repetidos na mesma operação.
- Não permitir empréstimo de exemplares indisponíveis.
- Não permitir data prevista anterior à data do empréstimo.
- Registrar a operação no log.

Utilizar `transaction.atomic()` para garantir a atomicidade.

Utilizar `select_for_update()` sobre os exemplares envolvidos para evitar condições de corrida em operações simultâneas.

As regras deverão ser implementadas em uma camada de serviços reutilizável pela API e pelas interfaces administrativas.

### 7.5 Devoluções

Implementar uma operação específica de devolução.

Ao devolver um empréstimo:

- Registrar a data de devolução.
- Atualizar a situação dos exemplares.
- Registrar o evento no log.
- Atualizar os indicadores do dashboard.

Não permitir devoluções duplicadas.

Considerar um empréstimo ativo quando `data_devolucao` estiver nula.

**Importante:** o banco original registra a devolução no cabeçalho do empréstimo. Portanto, a devolução deverá abranger todos os exemplares associados à operação.

Não implementar devolução parcial sem autorização para modificar o esquema.

### 7.6 Reservas

Implementar gerenciamento de reservas utilizando `tb_reserva`.

Funcionalidades:

- Criar reserva.
- Consultar reservas por usuário.
- Consultar reservas por livro.
- Cancelar reserva.
- Atender reserva.
- Visualizar reservas pendentes.

Definir estados consistentes, como:

- Pendente.
- Atendida.
- Cancelada.

A reserva deverá ser associada ao livro, conforme o esquema original, e não diretamente a um exemplar.

Impedir transições inválidas.

Adotar uma política simples de atendimento, preferencialmente respeitando a ordem de criação.

### 7.7 Logs

Utilizar `tb_log_sistema` para registrar eventos relevantes.

Implementar consulta administrativa com paginação e filtros.

Os registros deverão ser gerados automaticamente pelos serviços de negócio.

Não disponibilizar edição ou exclusão arbitrária dos logs.

---

## 8. API REST

Utilizar Django REST Framework.

Criar serializers, views e rotas organizadas por recurso.

Endpoints sugeridos:

| Recurso | Endpoint |
|---|---|
| Autenticação | `/api/auth/` |
| Usuários | `/api/usuarios/` |
| Alunos | `/api/alunos/` |
| Instituições | `/api/instituicoes/` |
| Cursos | `/api/cursos/` |
| Editoras | `/api/editoras/` |
| Categorias | `/api/categorias/` |
| Autores | `/api/autores/` |
| Livros | `/api/livros/` |
| Exemplares | `/api/exemplares/` |
| Reservas | `/api/reservas/` |
| Empréstimos | `/api/emprestimos/` |
| Logs | `/api/logs/` |

Utilizar ViewSets e Routers quando isso simplificar a implementação.

### Endpoints de negócio

Além do CRUD convencional, disponibilizar operações específicas:

```http
POST /api/emprestimos/
POST /api/emprestimos/{id}/devolucao/

POST /api/reservas/
POST /api/reservas/{id}/cancelamento/
POST /api/reservas/{id}/atendimento/

GET /api/livros/{id}/exemplares/
GET /api/emprestimos/atrasados/
GET /api/dashboard/
```

Implementar:

- Paginação.
- Filtros.
- Pesquisa.
- Ordenação.
- Validação dos dados.
- Respostas HTTP apropriadas.
- Autenticação e permissões.

Utilizar serializers separados dos modelos.

Não retornar hashes de senha.

Disponibilizar documentação OpenAPI, preferencialmente utilizando `drf-spectacular`, com Swagger UI acessível em `/api/docs/`.

A API deverá ser utilizável independentemente do frontend.

---

## 9. Frontend

Utilizar Django Templates, Bootstrap 5 e JavaScript vanilla.

Não criar uma SPA nem introduzir um processo de build JavaScript desnecessário.

O frontend deverá ser servido pelo próprio Django.

### Páginas obrigatórias

#### Dashboard

Apresentar:

- Quantidade de livros.
- Quantidade de exemplares.
- Exemplares disponíveis.
- Empréstimos ativos.
- Empréstimos atrasados.
- Reservas pendentes.
- Movimentações recentes.

#### Catálogo

Disponibilizar pesquisa de livros, filtros, detalhes bibliográficos e disponibilidade.

#### Empréstimos

Criar uma interface própria para selecionar usuários e exemplares, registrar empréstimos e realizar devoluções.

#### Reservas

Permitir cadastrar, consultar, atender e cancelar reservas.

#### Cadastros

Disponibilizar acesso às operações administrativas das demais entidades, aproveitando o Django Admin quando apropriado.

#### Logs

Disponibilizar uma interface de consulta aos registros do sistema.

### Requisitos de interface

- Interface em português brasileiro.
- Layout responsivo.
- Navegação consistente.
- Formulários com validação.
- Mensagens de sucesso e erro.
- Confirmação para operações destrutivas.
- Indicadores visuais de disponibilidade.
- Paginação nas listagens.
- Estados de carregamento.

As páginas deverão consumir os endpoints da API nas operações principais, utilizando `fetch()` quando apropriado.

Para autenticação baseada em sessão, utilizar os mecanismos de CSRF do Django.

Não duplicar regras de negócio nas views HTML ou no JavaScript.

---

## 10. Banco de dados e Docker

Criar um arquivo `compose.yaml` para executar PostgreSQL.

Configurar:

- Volume persistente.
- Variáveis de ambiente.
- Porta configurável.
- Healthcheck.
- Nome de banco dedicado ao projeto.

Disponibilizar `.env.example`.

O projeto deverá poder ser executado localmente com comandos equivalentes a:

```bash
docker compose up -d postgres

uv sync

uv run python manage.py migrate

uv run python manage.py runserver
```

O banco deverá ser criado pelas migrations do Django.

### Autorização para testes

O Coding Agent poderá executar o PostgreSQL utilizando Docker para desenvolver e validar a aplicação.

Caso não tenha acesso ao Docker ou permissões suficientes, deverá solicitar ao usuário que execute os comandos necessários.

Não assumir que o banco está funcionando sem verificar a conexão.

Não remover volumes ou bancos preexistentes sem autorização explícita.

---

## 11. Dados de demonstração

Criar um comando Django personalizado:

```bash
uv run python manage.py seed
```

O comando deverá popular o banco com dados fictícios suficientes para demonstrar todas as funcionalidades.

Incluir:

- Instituições.
- Cursos.
- Usuários.
- Alunos.
- Editoras.
- Categorias.
- Autores.
- Livros com múltiplos autores.
- Exemplares.
- Empréstimos ativos.
- Empréstimos concluídos.
- Empréstimos atrasados.
- Reservas pendentes e concluídas.
- Registros de log.

O seed deverá ser reproduzível e seguro para reexecução.

Não inserir senhas em texto puro.

---

## 12. Testes

Utilizar pytest e pytest-django.

Os testes deverão cobrir principalmente as regras de negócio.

Cenários mínimos:

1. Criação de usuários e alunos.
2. Cadastro de livros com múltiplos autores.
3. Cadastro de exemplares.
4. Realização de empréstimo.
5. Tentativa de emprestar um exemplar indisponível.
6. Tentativa de empréstimo sem itens.
7. Devolução de empréstimo.
8. Tentativa de devolução duplicada.
9. Criação e cancelamento de reservas.
10. Identificação de empréstimos atrasados.
11. Registro de logs.
12. Autenticação e proteção dos endpoints.
13. Integridade referencial.
14. Concorrência em operações de empréstimo.

Executar os testes contra PostgreSQL, evitando depender exclusivamente de SQLite, pois existem diferenças importantes no comportamento transacional e no bloqueio de registros.

Também validar a aplicação manualmente através do frontend.

Não considerar o projeto concluído apenas porque as migrations foram executadas com sucesso.

---

## 13. Documentação

Criar um README completo contendo:

- Descrição do projeto.
- Tecnologias utilizadas.
- Requisitos de instalação.
- Configuração do ambiente.
- Instalação das dependências com uv.
- Inicialização do PostgreSQL.
- Execução das migrations.
- Execução do seed.
- Criação de usuário administrativo.
- Inicialização da aplicação.
- Acesso ao Django Admin.
- Acesso ao frontend.
- Acesso à documentação da API.
- Execução dos testes.

Documentar as diferenças entre o esquema SQL Server original e sua implementação PostgreSQL.

Registrar também decisões de modelagem e regras de negócio não explicitamente definidas pelo SQL original.

---

## 14. Critérios de conclusão

O projeto somente será considerado concluído quando:

- As 14 tabelas originais estiverem implementadas.
- Os relacionamentos e constraints estiverem preservados.
- A stored procedure possuir implementação equivalente.
- As migrations funcionarem em um banco PostgreSQL vazio.
- O Django Admin estiver configurado para as entidades apropriadas.
- A autenticação estiver funcional.
- A API REST estiver implementada e documentada.
- O frontend estiver integrado à API.
- Os fluxos de empréstimo, devolução e reserva estiverem funcionais.
- Os dados de demonstração puderem ser carregados.
- As regras de integridade estiverem implementadas.
- Os testes essenciais estiverem passando.
- A aplicação puder ser executada seguindo o README.

Todas as tabelas deverão possuir utilização real, seja através das interfaces administrativas, das páginas próprias ou dos fluxos de negócio.

---

## 15. Instruções finais ao Coding Agent

Leia integralmente o arquivo `sqlserver.sql` antes de iniciar qualquer implementação.

Não desenvolva uma modelagem genérica de biblioteca ignorando a estrutura fornecida. O aproveitamento integral do banco original é o requisito central deste projeto.

Utilize Django de maneira idiomática, aproveitando seus recursos nativos de ORM, autenticação, formulários, migrations e administração.

Priorize código simples e organizado.

Não introduza microsserviços, Celery, Redis, filas, frontend JavaScript separado ou outras tecnologias que não sejam necessárias para cumprir os requisitos.

Não utilize o Django Admin como substituto para os fluxos principais de empréstimo, devolução e reserva.

Não modifique silenciosamente a estrutura original do banco. Caso alguma alteração seja tecnicamente necessária, justifique e documente a decisão.

O agente deverá implementar a aplicação de ponta a ponta, executar as validações disponíveis e corrigir os problemas identificados.

Ao finalizar, apresentar:

1. Resumo das funcionalidades implementadas.
2. Estrutura final do projeto.
3. Alterações realizadas em relação ao SQL original.
4. Instruções de execução.
5. Testes realizados e seus resultados.
6. Eventuais limitações ou pendências.

O resultado esperado é uma aplicação acadêmica de gerenciamento de bibliotecas completa, funcional e demonstrável, utilizando Django, Django REST Framework, PostgreSQL e uv.

<!-------------------------------------------------------------------------------------------->

# Solicitação de alteração — Autenticação e simplificação do Dashboard

Realize as seguintes modificações no projeto Django existente, preservando todas as funcionalidades já implementadas.

## 1. Restringir o acesso ao Dashboard

O Dashboard deverá ser acessível exclusivamente por usuários autenticados.

Requisitos:

- Usuários não autenticados deverão ser redirecionados para a página de login ao tentar acessar o Dashboard, inclusive diretamente pela URL.
- Após a autenticação, o usuário poderá ser redirecionado para a página originalmente solicitada.
- Nenhum dado, indicador ou estatística do Dashboard deverá ser disponibilizado a usuários não autenticados.
- Proteger também os endpoints da API utilizados pelo Dashboard, retornando `401 Unauthorized` ou `403 Forbidden`, conforme o mecanismo de autenticação utilizado.
- A proteção deverá ocorrer no backend, não apenas ocultando elementos no frontend.
- Não alterar desnecessariamente o comportamento das demais páginas.

## 2. Simplificar a página inicial (index)

Remover completamente o card intitulado **"Arquitetura do sistema"** da página inicial.

Entretanto, preservar os botões existentes:

- Swagger UI.
- Django Admin.

Esses botões deverão continuar visíveis, funcionais e com seus respectivos destinos inalterados.

Reorganizar o layout caso necessário para evitar espaços vazios após a remoção do card.

## 3. Validação

Após implementar as alterações, verificar:

1. Um visitante não autenticado não consegue visualizar o Dashboard nem obter seus dados pela API.
2. O acesso direto à URL do Dashboard redireciona corretamente para o login.
3. Usuários autenticados continuam acessando o Dashboard normalmente.
4. O card "Arquitetura do sistema" não aparece mais no index.
5. Os botões Swagger UI e Django Admin continuam presentes e funcionais.

**Importante:** realize apenas as alterações solicitadas e os ajustes estritamente necessários para implementá-las. Não refatore componentes não relacionados, não modifique o esquema do banco de dados e não remova funcionalidades existentes.

<!-------------------------------------------------------------------------------------------->

# Solicitação de alteração — Catálogo público e controle de acesso

Modificar o projeto Django existente para permitir que visitantes não autenticados consultem informações públicas da biblioteca, mantendo as operações de empréstimo e gerenciamento restritas a usuários autenticados.

## 1. Dashboard e página inicial

Permitir que visitantes não autenticados acessem a página inicial e visualizem exclusivamente os seguintes indicadores:

- Quantidade total de títulos cadastrados no catálogo.
- Quantidade de exemplares atualmente disponíveis.

Não disponibilizar aos visitantes informações sobre usuários, alunos, empréstimos, reservas, logs ou movimentações internas.

Usuários autenticados deverão continuar visualizando o Dashboard completo, conforme implementado anteriormente.

Manter a remoção do card **"Arquitetura do sistema"**, preservando os botões Swagger UI e Django Admin.

## 2. Catálogo público

Permitir que qualquer visitante, mesmo sem autenticação, acesse uma página de consulta ao catálogo da biblioteca.

Essa página deverá apresentar:

- Lista dos livros cadastrados.
- Título de cada livro.
- Informações bibliográficas públicas, quando disponíveis.
- Quantidade de exemplares disponíveis por título.
- Pesquisa de livros por título.
- Paginação, caso necessária.

Não expor informações pessoais dos usuários, histórico de empréstimos ou dados administrativos.

A disponibilidade deverá ser calculada a partir da situação real dos exemplares, evitando apresentar quantidades desatualizadas.

## 3. Empréstimos e operações restritas

A consulta pública ao catálogo **não deverá permitir que visitantes realizem empréstimos**.

Regras:

- Usuários não autenticados poderão consultar os livros e sua disponibilidade.
- Ações relacionadas a empréstimos deverão exigir autenticação.
- Caso exista um botão de empréstimo no catálogo público, apresentá-lo como "Entrar para solicitar empréstimo", direcionando o visitante para o login.
- Após autenticar-se, o usuário poderá retornar à página originalmente solicitada.
- Operações de cadastro, edição, exclusão, reservas, devoluções e gerenciamento deverão continuar protegidas conforme as permissões já existentes.

As restrições deverão ser aplicadas também nos endpoints da API, não apenas na interface.

## 4. API REST

Ajustar as permissões do Django REST Framework para permitir acesso público somente aos dados necessários.

Os endpoints públicos deverão disponibilizar exclusivamente informações autorizadas, utilizando serializers específicos quando necessário.

Não liberar indiscriminadamente os ViewSets existentes por meio de `AllowAny`.

Preservar as restrições de autenticação para operações de escrita e endpoints administrativos.

## 5. Validação

Verificar os seguintes cenários:

1. Visitantes conseguem acessar a página inicial.
2. Visitantes visualizam apenas os dois indicadores públicos.
3. Visitantes conseguem consultar e pesquisar o catálogo.
4. A quantidade de exemplares disponíveis está correta.
5. Visitantes não conseguem realizar empréstimos, inclusive através de requisições diretas à API.
6. Usuários autenticados continuam utilizando normalmente todas as funcionalidades anteriormente disponíveis.
7. O card "Arquitetura do sistema" permanece removido.
8. Os botões Swagger UI e Django Admin continuam presentes e funcionais.

**Importante:** realizar alterações pontuais, reutilizando os componentes e serviços existentes. Não modificar o esquema do banco de dados nem refatorar funcionalidades não relacionadas.
