from django.contrib.auth import authenticate, login, logout
from rest_framework import viewsets, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from .models import Usuario, Aluno
from .serializers import UsuarioSerializer, AlunoSerializer, LoginSerializer

class UsuarioViewSet(viewsets.ModelViewSet):
    """
    CRUD completo de Usuários (restrito a usuários autenticados).
    """
    permission_classes = [permissions.IsAuthenticated]
    queryset = Usuario.objects.all().order_by('nome')
    serializer_class = UsuarioSerializer
    search_fields = ['nome', 'email']
    ordering_fields = ['id_usuario', 'nome', 'email']


class AlunoViewSet(viewsets.ModelViewSet):
    """
    CRUD completo de Alunos, com dados acadêmicos associados (restrito a usuários autenticados).
    """
    permission_classes = [permissions.IsAuthenticated]
    queryset = Aluno.objects.select_related('usuario', 'curso', 'curso__instituicao').all().order_by('usuario__nome')
    serializer_class = AlunoSerializer
    search_fields = ['usuario__nome', 'usuario__email', 'matricula', 'curso__nome']
    filterset_fields = ['curso', 'curso__instituicao']
    ordering_fields = ['id_aluno', 'matricula', 'usuario__nome']


class LoginAPIView(APIView):
    """Endpoint para autenticação de usuários."""
    permission_classes = [permissions.AllowAny]

    @extend_schema(request=LoginSerializer, responses={200: UsuarioSerializer})
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        senha = serializer.validated_data['senha']

        user = authenticate(request, username=email, password=senha)
        if not user:
            # Fallback authenticate with email
            user = authenticate(request, email=email, password=senha)

        if user:
            login(request, user)
            return Response({
                'mensagem': 'Login realizado com sucesso.',
                'usuario': UsuarioSerializer(user).data
            }, status=status.HTTP_200_OK)

        return Response(
            {'erro': 'Credenciais inválidas. Verifique o e-mail e a senha.'},
            status=status.HTTP_401_UNAUTHORIZED
        )


class LogoutAPIView(APIView):
    """Endpoint para encerramento de sessão."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        logout(request)
        return Response({'mensagem': 'Logout realizado com sucesso.'}, status=status.HTTP_200_OK)


class MeAPIView(APIView):
    """Retorna os dados do usuário autenticado atual."""
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(responses={200: UsuarioSerializer})
    def get(self, request):
        return Response(UsuarioSerializer(request.user).data)
