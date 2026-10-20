from datetime import date
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions

from apps.catalogo.models import Livro, Exemplar, SituacaoExemplar, Autor, Editora, Categoria
from apps.circulacao.models import Emprestimo, Reserva, SituacaoReserva
from apps.auditoria.models import LogSistema
from apps.usuarios.models import Usuario

class DashboardAPIView(APIView):
    """
    Retorna métricas para o dashboard.
    Visitantes não autenticados têm acesso exclusivamente aos indicadores públicos:
    total_livros e exemplares_disponiveis.
    Usuários autenticados visualizam o conjunto completo de indicadores.
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        total_livros = Livro.objects.count()
        exemplares_disponiveis = Exemplar.objects.filter(situacao=SituacaoExemplar.DISPONIVEL).count()

        if not request.user.is_authenticated:
            return Response({
                'total_livros': total_livros,
                'exemplares_disponiveis': exemplares_disponiveis,
            })

        hoje = date.today()
        total_exemplares = Exemplar.objects.count()
        exemplares_emprestados = Exemplar.objects.filter(situacao=SituacaoExemplar.EMPRESTADO).count()
        
        emprestimos_ativos = Emprestimo.objects.filter(data_devolucao__isnull=True).count()
        emprestimos_atrasados = Emprestimo.objects.filter(
            data_devolucao__isnull=True,
            data_prevista_devolucao__lt=hoje
        ).count()
        reservas_pendentes = Reserva.objects.filter(situacao=SituacaoReserva.PENDENTE).count()

        movimentacoes_recentes = []
        logs = LogSistema.objects.all().order_by('-data_registro')[:10]
        for l in logs:
            movimentacoes_recentes.append({
                'id_log': l.id_log,
                'data_registro': l.data_registro.strftime('%d/%m/%Y %H:%M:%S'),
                'id_aluno': int(l.id_aluno) if l.id_aluno else None,
                'descricao': l.descricao
            })

        return Response({
            'total_livros': total_livros,
            'total_exemplares': total_exemplares,
            'exemplares_disponiveis': exemplares_disponiveis,
            'exemplares_emprestados': exemplares_emprestados,
            'emprestimos_ativos': emprestimos_ativos,
            'emprestimos_atrasados': emprestimos_atrasados,
            'reservas_pendentes': reservas_pendentes,
            'movimentacoes_recentes': movimentacoes_recentes
        })


def dashboard_view(request):
    """View da página inicial. Acessível a visitantes e usuários autenticados."""
    return render(request, 'dashboard/index.html')


def catalogo_view(request):
    """View pública da listagem e busca do catálogo de livros."""
    categorias = Categoria.objects.all().order_by('descricao')
    editoras = Editora.objects.all().order_by('nome')
    return render(request, 'catalogo/livros.html', {
        'categorias': categorias,
        'editoras': editoras
    })


def livro_detalhe_view(request, livro_id):
    """View pública de detalhes de um livro específico e seus exemplares."""
    livro = get_object_or_404(
        Livro.objects.select_related('categoria', 'editora').prefetch_related('autores', 'exemplares'),
        pk=livro_id
    )
    return render(request, 'catalogo/livro_detalhe.html', {'livro': livro})


@login_required
def emprestimos_view(request):
    """View da listagem de empréstimos e devoluções (restrito a autenticados)."""
    return render(request, 'emprestimos/listagem.html')


@login_required
def novo_emprestimo_view(request):
    """View para registrar um novo empréstimo (restrito a autenticados)."""
    usuarios = Usuario.objects.all().order_by('nome')
    return render(request, 'emprestimos/novo.html', {'usuarios': usuarios})


@login_required
def reservas_view(request):
    """View do gerenciamento de reservas (restrito a autenticados)."""
    usuarios = Usuario.objects.all().order_by('nome')
    livros = Livro.objects.all().order_by('titulo')
    return render(request, 'reservas/index.html', {
        'usuarios': usuarios,
        'livros': livros
    })


@login_required
def logs_view(request):
    """View para consulta de logs do sistema (restrito a autenticados)."""
    return render(request, 'auditoria/logs.html')


def login_view(request):
    """View de autenticação web."""
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        senha = request.POST.get('senha', '').strip()
        user = authenticate(request, username=email, password=senha)
        if not user:
            user = authenticate(request, email=email, password=senha)

        if user:
            login(request, user)
            messages.success(request, f"Bem-vindo(a), {user.nome}!")
            next_url = request.GET.get('next', 'dashboard')
            return redirect(next_url)
        else:
            messages.error(request, "Credenciais inválidas. Verifique o e-mail e a senha.")

    return render(request, 'usuarios/login.html')


def logout_view(request):
    """View de logout web."""
    logout(request)
    messages.info(request, "Você encerrou a sessão.")
    return redirect('login')
