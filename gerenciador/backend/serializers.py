from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import MeuUsuario, Projeto, Tarefa

class MeuUsuarioSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    
    class Meta:
        model = MeuUsuario
        fields = ['id', 'username', 'password', 'email', 'first_name', 'last_name', 
                 'bio', 'data_cadastro', 'cpf', 'data_nascimento', 'idade', 'endereco']
        read_only_fields = ['id', 'data_cadastro']
        extra_kwargs = {
            'password': {'write_only': True}  # não pode ler a senha
        }
    
    def create(self, validated_data):
        password = validated_data.pop('password')
        user = MeuUsuario.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user


class ProjetoSerializer(serializers.ModelSerializer):
    usuario = serializers.StringRelatedField(read_only=True)  # Mostra o username em vez do ID
    total_tarefas = serializers.SerializerMethodField()
    tarefas_concluidas = serializers.SerializerMethodField()
    progresso = serializers.SerializerMethodField()
    
    class Meta:
        model = Projeto
        fields = ['id', 'nome', 'descricao', 'usuario', 'data_criacao', 'data_atualizacao', 
                 'status', 'total_tarefas', 'tarefas_concluidas', 'progresso']
        read_only_fields = ['id', 'data_criacao', 'data_atualizacao', 'usuario']
    
    def get_total_tarefas(self, obj):
        """Retorna o total de tarefas do projeto"""
        return obj.tarefas.count()
    
    def get_tarefas_concluidas(self, obj):
        """Retorna o número de tarefas concluídas"""
        return obj.tarefas.filter(concluida=True).count()
    
    def get_progresso(self, obj):
        """Calcula o progresso do projeto em porcentagem"""
        total = obj.tarefas.count()
        if total == 0:
            return 0
        concluidas = obj.tarefas.filter(concluida=True).count()
        return round((concluidas / total) * 100, 2)


class TarefaSerializer(serializers.ModelSerializer):
    projeto_nome = serializers.CharField(source='projeto.nome', read_only=True)
    
    class Meta:
        model = Tarefa
        fields = ['id', 'titulo', 'descricao', 'projeto', 'projeto_nome', 'concluida', 
                 'prioridade', 'data_criacao', 'data_conclusao']
        read_only_fields = ['id', 'data_criacao', 'data_conclusao']
    
    def validate_projeto(self, value):
        """Valida se o projeto existe e pertence ao usuário autenticado"""
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            if value.usuario != request.user:
                raise serializers.ValidationError("Você não pode criar tarefas em projetos de outros usuários.")
        return value


class TarefaCreateSerializer(serializers.ModelSerializer):
    """Serializer simplificado para criar tarefas através do endpoint aninhado"""
    projeto_nome = serializers.CharField(source='projeto.nome', read_only=True)
    
    class Meta:
        model = Tarefa
        fields = ['id', 'titulo', 'descricao', 'projeto_nome', 'concluida', 
                 'prioridade', 'data_criacao', 'data_conclusao']
        read_only_fields = ['id', 'data_criacao', 'data_conclusao', 'projeto_nome']
        # Não inclui 'projeto' pois será definido automaticamente


class TarefaSimpleSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listar tarefas dentro de projetos"""
    class Meta:
        model = Tarefa
        fields = ['id', 'titulo', 'concluida', 'prioridade', 'data_criacao']

