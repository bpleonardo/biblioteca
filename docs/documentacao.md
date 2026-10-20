# Documentação acadêmica - Sistema de Gerenciamento de Biblioteca

## 1. Apresentação do projeto

### 1.1 Introdução e contextualização

O Sistema de Gerenciamento de Biblioteca é uma aplicação web para consulta do acervo, controle de exemplares físicos, empréstimos, devoluções, reservas e rastreabilidade de eventos. O problema tratado é a necessidade de centralizar o catálogo e as operações de circulação, reduzindo a inconsistência entre a disponibilidade informada e a disponibilidade efetiva de cada exemplar.

O sistema possui uma área pública de consulta e uma área autenticada destinada à operação e à gestão. A documentação descreve somente evidências encontradas no código-fonte, nos testes e no esquema de dados do repositório.

### 1.2 Objetivos

O objetivo geral é disponibilizar uma aplicação web para gerenciar um acervo bibliográfico e sua circulação. São objetivos específicos: permitir a consulta pública do catálogo e de indicadores resumidos; autenticar usuários; manter cadastros acadêmicos e bibliográficos; registrar empréstimos e devoluções com consistência transacional; administrar reservas; e registrar operações em log consultável.

### 1.3 Justificativa, escopo e limitações

A solução concentra informações de obras, autores, editoras, categorias, exemplares, usuários e movimentos de circulação em banco relacional. O escopo implementado não comprova, por si só, políticas como limite de empréstimos por pessoa, multa, prazo fixo obrigatório, fila de reservas, notificações ou autorização por papéis de negócio. Embora a interface mencione "Gestão Cadastral", o modelo `Usuario` expõe propriedades administrativas para todos os usuários e as APIs restritas usam autenticação, não uma separação de perfis como bibliotecário, aluno e administrador. Portanto, não há evidência para documentar essas distinções como permissões implementadas.

O documento de apoio do PIM fornecido trata de uma barbearia e não do sistema Biblioteca. Foi utilizado somente como referência de organização acadêmica; seus requisitos, tecnologias e dados não foram transferidos para este artefato.

### 1.4 Visão da solução e tecnologias

A solução é um monólito Django organizado em aplicativos: `core`, `usuarios`, `academico`, `catalogo`, `circulacao` e `auditoria`. O frontend é renderizado por Django Templates, com Bootstrap 5.3.3 e JavaScript puro. A API é REST com Django REST Framework, filtros, busca, ordenação e paginação; o contrato é exposto por drf-spectacular/Swagger. O banco é PostgreSQL, acessado pelo ORM Django e pelo driver psycopg. Docker Compose fornece um PostgreSQL opcional para execução. Os testes usam pytest e pytest-django.

O projeto preserva a origem SQL Server em PostgreSQL: nomes físicos de tabelas, nulabilidade e a chave composta de `tb_livros_autores`, implementada com `CompositePrimaryKey`. A escolha de serviços de circulação com `transaction.atomic()` e `select_for_update()` protege a alteração de disponibilidade contra concorrência.

## 2. Requisitos levantados

### 2.1 Requisitos funcionais

| ID | Descrição | Prioridade |
|---|---|---|
| RF001 | Exibir, sem autenticação, o total de títulos e de exemplares disponíveis. | Alta |
| RF002 | Permitir consultar, pesquisar e filtrar o catálogo por texto, categoria, editora e autor. | Alta |
| RF003 | Exibir detalhes da obra, autores, editora, categoria e exemplares. | Alta |
| RF004 | Autenticar e encerrar sessões por e-mail e senha, tanto pela interface web quanto pela API. | Alta |
| RF005 | Expor dados do usuário autenticado e o painel completo de indicadores após login. | Média |
| RF006 | Permitir a usuários autenticados manter editoras, categorias, autores, livros e exemplares pela API; a interface também oferece cadastro de livro e exemplar. | Alta |
| RF007 | Permitir manter instituições, cursos, usuários e alunos pela API autenticada e pelo Django Admin. | Média |
| RF008 | Registrar empréstimo para um usuário com um ou mais exemplares e data prevista de devolução. | Alta |
| RF009 | Registrar a devolução integral de todos os itens de um empréstimo. | Alta |
| RF010 | Consultar empréstimos e filtrar os atrasados. | Média |
| RF011 | Criar, cancelar e atender reservas de obras para usuários autenticados. | Média |
| RF012 | Registrar e consultar logs de eventos de circulação. | Média |
| RF013 | Disponibilizar documentação OpenAPI e Swagger da API. | Baixa |

### 2.2 Requisitos não funcionais

| ID | Descrição | Prioridade |
|---|---|---|
| RNF001 | Utilizar PostgreSQL e preservar o esquema físico legado mapeado pelo projeto. | Alta |
| RNF002 | Executar empréstimos e devoluções de forma atômica. | Alta |
| RNF003 | Bloquear linhas de exemplares durante a concessão do empréstimo para evitar concorrência. | Alta |
| RNF004 | Restringir as operações privadas da web e da API a sessão autenticada. | Alta |
| RNF005 | Armazenar senhas com hash, sem expor o hash nos serializadores de resposta. | Alta |
| RNF006 | Fornecer API paginada (20 registros por página), filtrável, pesquisável e ordenável quando configurado. | Média |
| RNF007 | Usar interface responsiva baseada em Bootstrap e idioma/configuração regional pt-BR. | Média |
| RNF008 | Manter rastreabilidade por procedure de log PostgreSQL. | Média |

### 2.3 Regras de negócio

| ID | Regra efetivamente implementada |
|---|---|
| RN001 | Um empréstimo deve conter ao menos um exemplar. |
| RN002 | Um mesmo exemplar não pode ser repetido na mesma solicitação. |
| RN003 | A data prevista não pode anteceder a data do empréstimo. |
| RN004 | O usuário e todos os exemplares informados devem existir. |
| RN005 | Só pode ser emprestado exemplar com situação `Disponível` e sem item de empréstimo ativo. |
| RN006 | Ao criar empréstimo, cada exemplar é marcado como `Emprestado`; ao devolver, todos os itens do empréstimo retornam a `Disponível`. |
| RN007 | Uma devolução já concluída não pode ser repetida. |
| RN008 | Um empréstimo ativo torna-se atrasado quando a data atual é posterior à data prevista de devolução. |
| RN009 | Somente reserva pendente pode ser cancelada ou atendida; uma reserva não é automaticamente atendida pela criação de empréstimo. |
| RN010 | Empréstimos, devoluções, criação, cancelamento e atendimento de reserva registram logs via `sp_reg_log_sistema`. |

## 3. Usuários e personas

Não há papéis de negócio distintos implementados. Para representar o uso observado, as personas a seguir distinguem o contexto de uso, não permissões adicionais.

### 3.1 Marina Alves - visitante pesquisadora

Perfil e contexto: estudante que verifica previamente a existência de uma obra. Objetivos: localizar título, ISBN, autor ou categoria e saber se há exemplares disponíveis. Necessidades: acesso sem login, busca e detalhes de obra. Dificuldades: não poder registrar circulação sem sessão. Funcionalidades aderentes: dashboard público, catálogo, filtros e detalhe de livro.

### 3.2 Rafael Costa - operador autenticado

Perfil e contexto: pessoa que executa o atendimento no balcão. Objetivos: localizar usuário e exemplar, registrar empréstimo ou devolução e acompanhar pendências. Necessidades: lista de exemplares disponíveis, validação imediata e painel de circulação. Dificuldades: a operação bloqueia itens indisponíveis, o que exige selecionar outro exemplar. Funcionalidades aderentes: novo empréstimo, listagem, devolução, filtro de atrasados e reservas.

### 3.3 Camila Nunes - responsável pelo acervo

Perfil e contexto: usuária autenticada que atualiza dados bibliográficos e consulta histórico operacional. Objetivos: cadastrar obras/exemplares e rastrear eventos. Necessidades: acesso ao catálogo, Django Admin e logs. Dificuldades: o código não oferece um papel exclusivo de gestão; qualquer usuário autenticado recebe as permissões de API descritas. Funcionalidades aderentes: cadastro de obra/exemplar, APIs CRUD, gestão cadastral e logs.

## 4. Interfaces e wireframes

Os wireframes editáveis representam a hierarquia encontrada nos templates: navegação, filtros, tabelas, formulários e ações. São esquemáticos e não redesenham a aplicação.

| Figura | Artefato | Finalidade |
|---|---|---|
| Figura 1 | [Início não autenticado](wireframes/inicio-nao-autenticado.excalidraw) | Indicadores públicos, acesso ao catálogo e ações de entrada. |
| Figura 2 | [Início autenticado](wireframes/inicio-autenticado.excalidraw) | Painel consolidado, movimentações recentes e ações rápidas. |
| Figura 3 | [Realização de empréstimo](wireframes/realizacao-emprestimo.excalidraw) | Seleção de usuário, consulta de exemplares e resumo da operação. |

## 5. Modelagem e diagramas

### 5.1 Banco de dados

A [Figura 4 - modelo de banco de dados](diagramas/banco-de-dados.dbml) usa DBML, formato compatível com o dbdiagram.io. O arquivo contém as 14 tabelas físicas, todas as colunas mapeadas no esquema do projeto, chaves, restrições relevantes, valores padrão e referências. `tb_livros_autores` possui chave primária composta por `id_livro` e `id_autor`. `tb_log_sistema` não possui referência de usuário porque `id_aluno` é um campo histórico sem chave estrangeira no esquema real.

### 5.2 Classes e responsabilidades

A [Figura 5 - classes](diagramas/classes.mmd) concentra modelos do domínio e o serviço de circulação. O arquivo foi revisado para utilizar declarações de membros em blocos e rótulos de cardinalidade compatíveis com Mermaid. As propriedades `is_ativo` e `is_atrasado` são derivadas de datas; o serviço encapsula as transações e os modelos persistem os dados.

### 5.3 Arquitetura C4

- [Figura 6 - contexto (C1)](diagramas/c4-contexto.mmd): atores e fronteira do sistema.
- [Figura 7 - contêineres (C2)](diagramas/c4-containers.mmd): navegador, aplicação, banco e documentação de API.
- [Figura 8 - componentes (C3)](diagramas/c4-componentes.mmd): módulos internos e dependências relevantes; cada aplicativo inclui o prefixo `app:` e seu identificador técnico.
- [Figura 9 - visão macro](diagramas/c4-macro.mmd): representação C4 integrada dos atores, interface, API, módulos do monólito Django, banco de dados, Swagger e Django Admin. Sua finalidade é explicar as relações entre os elementos, não substituir os diagramas C1-C3 mais focados.

### 5.4 Sequência de empréstimo

A [Figura 10 - sequência](diagramas/sequencia-emprestimo.mmd) explicita autenticação prévia na camada de endpoint, validações, bloqueio de linha, persistência, atualização de situação e alternativas de erro. A operação devolve HTTP 400 para `ValidationError` e 201 em caso de criação.

### 5.5 Casos de uso e navegação

A [Figura 11 - casos de uso](diagramas/casos-de-uso.puml) é PlantUML, escolhido por ser uma notação UML editável e expressar claramente fronteira, atores e `include`. A [Figura 12 - fluxo de navegação](diagramas/fluxo-navegacao.mmd) separa páginas públicas das restritas.

## 6. Segurança, decisões e limitações técnicas

O middleware de autenticação do Django, CSRF e sessões são configurados. A API utiliza `SessionAuthentication` e `BasicAuthentication`; operações que modificam cadastro no catálogo/academia requerem autenticação, e empréstimos, reservas, usuários, alunos e logs usam `IsAuthenticated`. A senha do usuário é gravada no campo físico `senha` mediante `set_password`; o serializer não a retorna.

A procedure `sp_reg_log_sistema` é recriada por migration e chamada pelo serviço de auditoria. Há uma particularidade preservada: o argumento de usuário é gravado em `tb_log_sistema.id_aluno`. Essa nomenclatura não deve ser interpretada como uma relação FK garantida.

O código declara que o modelo preserva estritamente as quatro colunas de usuário e implementa propriedades `is_staff`, `is_active` e `is_superuser` como verdadeiras. Documentar isso como um controle de acesso de administrador seria incorreto: é uma compatibilidade para Django Admin, não uma política de autorização granular.

## 7. Validação dos artefatos

O modelo de dados foi migrado para DBML e pode ser importado no dbdiagram.io; o antigo ERD Mermaid foi removido para evitar versões concorrentes. Os demais diagramas Mermaid permanecem em arquivos `.mmd`; a visão macro emprega a sintaxe C4 experimental documentada pelo Mermaid. O diagrama de casos de uso está em PlantUML editável porque Mermaid não oferece uma notação UML de casos de uso equivalente. Os wireframes foram reduzidos às três telas solicitadas e são arquivos JSON Excalidraw compostos exclusivamente por elementos nativos (`rectangle` e `text`).

Como não foi localizado um ambiente PostgreSQL configurado em execução nesta análise, a validação foi estática: leitura dos modelos, migrations, serviços, views, templates, testes e configurações. Não foram inferidos requisitos a partir do documento PIM anexo, pois ele descreve domínio distinto.

## Referências

DJANGO SOFTWARE FOUNDATION. *Django documentation*. Disponível em: <https://docs.djangoproject.com/>. Acesso em: 21 out. 2026.

MERMAID. *Mermaid documentation*. Disponível em: <https://mermaid.js.org/>. Acesso em: 21 out. 2026.

EXCALIDRAW. *JSON schema*. Disponível em: <https://docs.excalidraw.com/docs/codebase/json-schema>. Acesso em: 21 out. 2026.
