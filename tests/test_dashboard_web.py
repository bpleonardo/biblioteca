import pytest
from django.test import Client

@pytest.mark.django_db
def test_pagina_inicial_acesso_visitante_publico():
    """Validação 1 e 2: Visitante acessa página inicial e visualiza apenas os 2 indicadores públicos."""
    client = Client()
    res = client.get('/')
    assert res.status_code == 200

    html = res.content.decode('utf-8')

    # Indicadores públicos presentes
    assert 'Títulos no Catálogo' in html
    assert 'Exemplares Disponíveis' in html

    # Indicadores e áreas privadas AUSENTES para visitantes
    assert 'Empréstimos Ativos' not in html
    assert 'Reservas Pendentes' not in html
    assert 'Últimas Movimentações Registradas' not in html

    # Card 'Arquitetura do sistema' permanece removido
    assert 'Arquitetura do Sistema' not in html
    assert 'Arquitetura do sistema' not in html

    # Botões Swagger UI e Django Admin presentes e funcionais
    assert 'href="/api/docs/"' in html
    assert 'Swagger UI' in html
    assert 'href="/admin/"' in html
    assert 'Django Admin' in html

@pytest.mark.django_db
def test_pagina_inicial_acesso_autenticado(usuario):
    """Validação 6: Usuário autenticado visualiza o Dashboard completo."""
    client = Client()
    client.force_login(usuario)
    res = client.get('/')
    assert res.status_code == 200

    html = res.content.decode('utf-8')

    # Todos os 4 indicadores presentes para autenticados
    assert 'Títulos no Catálogo' in html
    assert 'Exemplares Disponíveis' in html
    assert 'Empréstimos Ativos' in html
    assert 'Reservas Pendentes' in html
    assert 'Últimas Movimentações Registradas' in html

    # Card 'Arquitetura do sistema' permanece removido
    assert 'Arquitetura do Sistema' not in html
    assert 'Arquitetura do sistema' not in html

    # Botões Swagger UI e Django Admin presentes e funcionais
    assert 'href="/api/docs/"' in html
    assert 'Swagger UI' in html
    assert 'href="/admin/"' in html
    assert 'Django Admin' in html

@pytest.mark.django_db
def test_catalogo_publico_e_botao_emprestimo_visitante(livro, exemplares):
    """Validação 3: Consulta ao catálogo público e botão 'Entrar para solicitar empréstimo'."""
    client = Client()
    # Acesso à listagem pública do catálogo
    res_cat = client.get('/catalogo/')
    assert res_cat.status_code == 200

    # Acesso aos detalhes públicos da obra
    res_detalhe = client.get(f'/catalogo/livros/{livro.id_livro}/')
    assert res_detalhe.status_code == 200
    html = res_detalhe.content.decode('utf-8')
    assert livro.titulo in html

    # Botão de empréstimo deve convidar o visitante a entrar para solicitar empréstimo
    assert 'Entrar para solicitar empréstimo' in html
    assert '/login/?next=' in html

@pytest.mark.django_db
def test_operacoes_restritas_redirecionam_visitante():
    """Validação 5: Páginas de empréstimo e circulação continuam exigindo login."""
    client = Client()
    for rota in ['/emprestimos/', '/emprestimos/novo/', '/reservas/', '/logs/']:
        res = client.get(rota, follow=False)
        assert res.status_code == 302
        assert '/login/' in res.headers['Location']
