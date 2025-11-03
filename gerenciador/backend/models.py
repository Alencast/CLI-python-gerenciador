from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.





class MeuUsuario(AbstractUser):
    bio = models.TextField(blank=True, null=True, help_text="Biografia do usuário")
    data_cadastro = models.DateTimeField(auto_now_add=True)
    cpf = models.CharField(max_length=11, blank=True, null=True, help_text="CPF do usuário")
    data_nascimento = models.DateField(blank=True, null=True, help_text="Data de nascimento")
    idade = models.IntegerField(blank=True, null=True, help_text="Idade do usuário")
    endereco = models.CharField(max_length=255, blank=True, null=True, help_text="Endereço completo")
    def __str__(self):
        return self.username
    


class Projeto(models.Model):
  
    STATUS_CHOICES = [
        ('planejamento', 'Planejamento'),
        ('em_andamento', 'Em Andamento'),
        ('concluido', 'Concluído'),
    ]
    
    nome = models.CharField(max_length=200, help_text="Nome do projeto")
    descricao = models.TextField(help_text="Descrição detalhada do projeto")
    usuario = models.ForeignKey(
        'MeuUsuario', 
        on_delete=models.CASCADE, 
        related_name='projetos',
        help_text="Usuário responsável pelo projeto"
    )
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='planejamento',
        help_text="Status atual do projeto"
    )
    
    def __str__(self):
        return self.nome
    
    class Meta:
        verbose_name = "Projeto"
        verbose_name_plural = "Projetos"
        ordering = ['-data_criacao']


class Tarefa(models.Model):
  
    PRIORIDADE_CHOICES = [
        ('baixa', 'Baixa'),
        ('media', 'Média'),
        ('alta', 'Alta'),
    ]
    
    titulo = models.CharField(max_length=200, help_text="Título da tarefa")
    descricao = models.TextField(help_text="Descrição detalhada da tarefa")
    projeto = models.ForeignKey(
        'Projeto', 
        on_delete=models.CASCADE, 
        related_name='tarefas',
        help_text="Projeto ao qual a tarefa pertence"
    )
    concluida = models.BooleanField(default=False, help_text="Indica se a tarefa foi concluída")
    prioridade = models.CharField(
        max_length=10, 
        choices=PRIORIDADE_CHOICES, 
        default='media',
        help_text="Prioridade da tarefa"
    )
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_conclusao = models.DateTimeField(
        null=True, 
        blank=True, 
        help_text="Data e hora quando a tarefa foi concluída"
    )
    
    def __str__(self):
        return f"{self.titulo} - {self.projeto.nome}"
    
    # def save(self, *args, **kwargs):
       
    #     if self.concluida and not self.data_conclusao:
    #         from django.utils import timezone
    #         self.data_conclusao = timezone.now()
    #     elif not self.concluida:
    #         self.data_conclusao = None
    #     super().save(*args, **kwargs)
    
    class Meta:
        verbose_name = "Tarefa"
        verbose_name_plural = "Tarefas"
        ordering = ['-data_criacao']