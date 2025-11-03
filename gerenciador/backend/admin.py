from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import MeuUsuario, Projeto, Tarefa

# Register your models here.


# admin.site.register(Usuario)
# admin.site.register(Projeto)
# admin.site.register(Tarefa)

@admin.register(MeuUsuario)
class MeuUsuarioAdmin(UserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_staff', 'data_cadastro']
    list_filter = ['is_staff', 'is_superuser', 'is_active', 'data_cadastro']
    search_fields = ['username', 'first_name', 'last_name', 'email']
    ordering = ['-data_cadastro']
    

    fieldsets = UserAdmin.fieldsets + (
        ('Informações Adicionais', {'fields': ('bio', 'data_cadastro')}),
    )
    
  
    readonly_fields = ['data_cadastro']


@admin.register(Projeto)
class ProjetoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'usuario', 'status', 'data_criacao', 'data_atualizacao']
    list_filter = ['status', 'data_criacao', 'usuario']
    search_fields = ['nome', 'descricao', 'usuario__username']
    ordering = ['-data_criacao']
    readonly_fields = ['data_criacao', 'data_atualizacao']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('usuario')


@admin.register(Tarefa)
class TarefaAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'projeto', 'prioridade', 'concluida', 'data_criacao', 'data_conclusao']
    list_filter = ['concluida', 'prioridade', 'data_criacao', 'projeto__status']
    search_fields = ['titulo', 'descricao', 'projeto__nome']
    ordering = ['-data_criacao']
    readonly_fields = ['data_criacao', 'data_conclusao']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('projeto', 'projeto__usuario')
    
   
    actions = ['marcar_como_concluida', 'marcar_como_pendente']
    
    def marcar_como_concluida(self, request, queryset):
        updated = queryset.update(concluida=True)
        self.message_user(request, f'{updated} tarefa(s) marcada(s) como concluída(s).')
    marcar_como_concluida.short_description = "Marcar tarefas selecionadas como concluídas"
    
    def marcar_como_pendente(self, request, queryset):
        updated = queryset.update(concluida=False)
        self.message_user(request, f'{updated} tarefa(s) marcada(s) como pendente(s).')
    marcar_como_pendente.short_description = "Marcar tarefas selecionadas como pendentes"

    