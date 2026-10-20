import pytest
from datetime import date, timedelta
from rest_framework import status
from apps.catalogo.models import SituacaoExemplar

@pytest.mark.django_db
def test_api_login_e_me(api_client, usuario):
    """Cenário 12: Autenticação via API REST."""
    res = api_client.post('/api/auth/login/', {
        'email': 'leitor@teste.com',
        'senha': 'segredo_teste'
    })
    assert res.status_code == status.HTTP_200_OK
    assert 'usuario' in res.data
    assert 'senha' not in res.data['usuario']
    assert 'password' not in res.data['usuario']

    res_me = api_client.get('/api/auth/me/')
    assert res_me.status_code == status.HTTP_200_OK
    assert res_me.data['email'] == 'leitor@teste.com'

@pytest.mark.django_db
def test_api_dashboard_deslogado_indicadores_publicos(api_client, livro, exemplares):
    """Validação 2: Visitante visualiza exclusivamente os 2 indicadores públicos sem dados internos."""
    res = api_client.get('/api/dashboard/')
    assert res.status_code == status.HTTP_200_OK

    # Indicadores públicos permitidos
    assert 'total_livros' in res.data
    assert 'exemplares_disponiveis' in res.data
    assert res.data['total_livros'] >= 1
    assert res.data['exemplares_disponiveis'] == 2

    # Dados privados bloqueados para visitantes
    assert 'emprestimos_ativos' not in res.data
    assert 'emprestimos_atrasados' not in res.data
    assert 'reservas_pendentes' not in res.data
    assert 'movimentacoes_recentes' not in res.data
    assert 'total_exemplares' not in res.data

@pytest.mark.django_db
def test_api_dashboard_metricas_autenticado(api_client, usuario, livro, exemplares):
    """Validação 6: Usuário autenticado visualiza todas as métricas consolidadas."""
    api_client.force_authenticate(user=usuario)
    res = api_client.get('/api/dashboard/')
    assert res.status_code == status.HTTP_200_OK
    assert 'total_livros' in res.data
    assert 'total_exemplares' in res.data
    assert 'exemplares_disponiveis' in res.data
    assert 'emprestimos_ativos' in res.data
    assert 'emprestimos_atrasados' in res.data
    assert 'reservas_pendentes' in res.data
    assert 'movimentacoes_recentes' in res.data

@pytest.mark.django_db
def test_api_catalogo_publico_consulta_e_pesquisa(api_client, livro, exemplares):
    """Validação 3 e 4: Visitante consulta e pesquisa o catálogo, com disponibilidade precisa."""
    # Consulta sem autenticação
    res = api_client.get('/api/livros/')
    assert res.status_code == status.HTTP_200_OK
    livros = res.data.get('results', res.data)
    assert len(livros) >= 1

    item = next(l for l in livros if l['id_livro'] == livro.id_livro)
    assert item['titulo'] == "Arquitetura de Software Moderna"
    # Disponibilidade calculada corretamente: 2 disponíveis de 3
    assert item['exemplares_disponiveis'] == 2
    assert item['total_exemplares'] == 3

    # Pesquisa pública por título
    res_busca = api_client.get('/api/livros/?search=Arquitetura')
    assert res_busca.status_code == status.HTTP_200_OK
    buscados = res_busca.data.get('results', res_busca.data)
    assert any(l['id_livro'] == livro.id_livro for l in buscados)

@pytest.mark.django_db
def test_api_visitante_bloqueado_em_operacoes_restritas(api_client, usuario, exemplares):
    """Validação 5: Visitantes não conseguem realizar empréstimos nem acessar dados privados via API."""
    ex = exemplares[0]
    payload = {
        'usuario_id': usuario.id_usuario,
        'exemplar_ids': [ex.id_exemplar],
        'data_prevista_devolucao': (date.today() + timedelta(days=10)).isoformat()
    }

    # Bloqueio em criação de empréstimo sem login
    res_post_emp = api_client.post('/api/emprestimos/', payload, format='json')
    assert res_post_emp.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]

    # Bloqueio em listagem de empréstimos sem login
    res_get_emp = api_client.get('/api/emprestimos/')
    assert res_get_emp.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]

    # Bloqueio em reservas sem login
    res_reserva = api_client.get('/api/reservas/')
    assert res_reserva.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]

    # Bloqueio em logs sem login
    res_logs = api_client.get('/api/logs/')
    assert res_logs.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]

    # Bloqueio em usuários/alunos sem login
    res_usuarios = api_client.get('/api/usuarios/')
    assert res_usuarios.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]

@pytest.mark.django_db
def test_api_fluxo_completo_emprestimo_e_devolucao_autenticado(api_client, usuario, exemplares):
    """Cenário de empréstimo e devolução funcional para usuário autenticado."""
    api_client.force_authenticate(user=usuario)

    ex = exemplares[0]
    payload = {
        'usuario_id': usuario.id_usuario,
        'exemplar_ids': [ex.id_exemplar],
        'data_prevista_devolucao': (date.today() + timedelta(days=10)).isoformat()
    }

    res_post = api_client.post('/api/emprestimos/', payload, format='json')
    assert res_post.status_code == status.HTTP_201_CREATED
    emp_id = res_post.data['id_emprestimo']

    ex.refresh_from_db()
    assert ex.situacao == SituacaoExemplar.EMPRESTADO

    # Devolver via API
    res_dev = api_client.post(f'/api/emprestimos/{emp_id}/devolucao/')
    assert res_dev.status_code == status.HTTP_200_OK
    assert res_dev.data['data_devolucao'] is not None

    ex.refresh_from_db()
    assert ex.situacao == SituacaoExemplar.DISPONIVEL
