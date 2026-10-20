from django.urls import path
from .views import (
    DashboardAPIView,
    dashboard_view,
    catalogo_view,
    livro_detalhe_view,
    emprestimos_view,
    novo_emprestimo_view,
    reservas_view,
    logs_view,
    login_view,
    logout_view
)

urlpatterns = [
    # API endpoints
    path('api/dashboard/', DashboardAPIView.as_view(), name='api-dashboard'),

    # Web Template Views
    path('', dashboard_view, name='dashboard'),
    path('catalogo/', catalogo_view, name='catalogo'),
    path('catalogo/livros/<int:livro_id>/', livro_detalhe_view, name='livro-detalhe'),
    path('emprestimos/', emprestimos_view, name='emprestimos'),
    path('emprestimos/novo/', novo_emprestimo_view, name='emprestimo-novo'),
    path('reservas/', reservas_view, name='reservas'),
    path('logs/', logs_view, name='logs'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
]
