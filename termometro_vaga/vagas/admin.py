from django.contrib import admin
from .models import Curso, Candidato

@admin.register(Curso)
class CursoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'total_vagas', 'vagas_ocupadas', 'vagas_disponiveis']

@admin.register(Candidato)
class CandidatoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'curso', 'tipo', 'status', 'data_inscricao']
    list_filter = ['status', 'tipo', 'curso']
    search_fields = ['nome', 'cpf', 'email']