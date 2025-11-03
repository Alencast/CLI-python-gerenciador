from django.shortcuts import get_object_or_404, render
from django.contrib.auth import authenticate
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, authentication_classes, permission_classes, action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import MeuUsuario, Projeto, Tarefa
from .serializers import MeuUsuarioSerializer, ProjetoSerializer, TarefaSerializer, TarefaCreateSerializer

# Create your views here.

@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
  
    username = request.data.get('username')
    password = request.data.get('password')
    
    if username is None or password is None:
        return Response({
            'error': 'Username e password são obrigatórios'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    user = authenticate(username=username, password=password)
    
    if user is not None:
        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
            }
        }, status=status.HTTP_200_OK)
    else:
        return Response({
            'error': 'Credenciais inválidas'
        }, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
@permission_classes([AllowAny])
def signup(request):
    #registrar usuario
    serializer = MeuUsuarioSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            'message': 'Usuário criado com sucesso',
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
            }
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def test_token(request):
    #view pra test
    return Response({
        'message': f'Token válido para o usuário: {request.user.username}',
        'user_id': request.user.id,
        'email': request.user.email
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def logout_view(request):
    
    #view do logout com blacklist
    try:
        refresh_token = request.data["refresh"]
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response({
            'message': 'Logout realizado com sucesso'
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'error': 'Token inválido'
        }, status=status.HTTP_400_BAD_REQUEST)


class MeuUsuarioViewSet(viewsets.ModelViewSet):
    queryset = MeuUsuario.objects.all()
    serializer_class = MeuUsuarioSerializer
    permission_classes = [IsAuthenticated]


class ProjetoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciar projetos
    Endpoints:
    - GET /api/projetos/ - Listar projetos do usuário autenticado
    - POST /api/projetos/ - Criar novo projeto
    - GET /api/projetos/{id}/ - Detalhes de um projeto
    - PUT /api/projetos/{id}/ - Atualizar projeto
    - DELETE /api/projetos/{id}/ - Deletar projeto
    - GET /api/projetos/{id}/tarefas/ - Listar tarefas do projeto
    - POST /api/projetos/{id}/tarefas/ - Criar nova tarefa no projeto
    """
    queryset = Projeto.objects.all()  # Queryset base (será filtrado no get_queryset)
    serializer_class = ProjetoSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
       #        Retorna apenas projetos do usuário autenticado

        return Projeto.objects.filter(usuario=self.request.user).order_by('-data_criacao')
    
    def perform_create(self, serializer):
        #        Automaticamente associa o projeto ao usuário autenticado

        serializer.save(usuario=self.request.user)
    
    def get_object(self):
        #        Retorna o objeto projeto, garantindo que pertence ao usuário autenticado

        obj = get_object_or_404(Projeto, pk=self.kwargs['pk'], usuario=self.request.user)
        return obj
    
    @action(detail=True, methods=['get', 'post'])
    def tarefas(self, request, pk=None):
        """
        Endpoint aninhado para gerenciar tarefas de um projeto específico
        GET /api/projetos/{id}/tarefas/ - Listar tarefas do projeto
        POST /api/projetos/{id}/tarefas/ - Criar nova tarefa no projeto
        """
        projeto = self.get_object()
        
        if request.method == 'GET':
            # Listar tarefas do projeto
            tarefas = Tarefa.objects.filter(projeto=projeto).order_by('-data_criacao')
            serializer = TarefaSerializer(tarefas, many=True)
            return Response(serializer.data)
        
        elif request.method == 'POST':
            # Criar nova tarefa no projeto
            serializer = TarefaCreateSerializer(data=request.data, context={'request': request})
            if serializer.is_valid():
                # Força o projeto a ser o projeto da URL
                tarefa = serializer.save(projeto=projeto)
                # Retorna com serializer completo incluindo projeto_nome
                response_serializer = TarefaSerializer(tarefa)
                return Response(response_serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TarefaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciar tarefas
    Endpoints:
    - GET /api/tarefas/ - Listar tarefas do usuário autenticado
    - POST /api/tarefas/ - Criar nova tarefa
    - GET /api/tarefas/{id}/ - Detalhes de uma tarefa
    - PUT /api/tarefas/{id}/ - Atualizar tarefa
    - PATCH /api/tarefas/{id}/concluir/ - Marcar tarefa como concluída
    - DELETE /api/tarefas/{id}/ - Deletar tarefa
    """
    queryset = Tarefa.objects.all()  # Queryset base (será filtrado no get_queryset)
    serializer_class = TarefaSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """
        Retorna apenas tarefas de projetos do usuário autenticado
        """
        projeto_id = self.request.query_params.get('projeto', None)
        queryset = Tarefa.objects.filter(projeto__usuario=self.request.user).order_by('-data_criacao')
        
        if projeto_id is not None:
            queryset = queryset.filter(projeto_id=projeto_id)
            
        return queryset
    
    def perform_create(self, serializer):
       #        Verifica se o projeto pertence ao usuário antes de criar a tarefa

        projeto = serializer.validated_data['projeto']
        if projeto.usuario != self.request.user:
            raise PermissionDenied("Você não pode criar tarefas em projetos de outros usuários")
        serializer.save()
    
    def get_object(self):
        #        Retorna o objeto tarefa, garantindo que pertence ao usuário autenticado

        obj = get_object_or_404(Tarefa, pk=self.kwargs['pk'], projeto__usuario=self.request.user)
        return obj
    
    @action(detail=True, methods=['patch'])
    def concluir(self, request, pk=None):
        
        tarefa = self.get_object()
        
        # Verifica se foi enviado um valor específico
        concluida = request.data.get('concluida', None)
        
        if concluida is not None:
            # Usa o valor enviado
            tarefa.concluida = bool(concluida)
        else:
            # Alterna o status atual
            tarefa.concluida = not tarefa.concluida
        
        # Atualiza data_conclusao automaticamente
        if tarefa.concluida and not tarefa.data_conclusao:
            from django.utils import timezone
            tarefa.data_conclusao = timezone.now()
        elif not tarefa.concluida:
            tarefa.data_conclusao = None
            
        tarefa.save()
        
        serializer = self.get_serializer(tarefa)
        return Response({
            'message': f'Tarefa {"concluída" if tarefa.concluida else "marcada como pendente"}',
            'tarefa': serializer.data
        })


