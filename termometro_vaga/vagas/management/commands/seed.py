from django.core.management.base import BaseCommand
from vagas.models import Curso

class Command(BaseCommand):
    help = 'Cria cursos de exemplo'

    def handle(self, *args, **options):
        dados = [
            {'nome': 'Análise e Desenvolvimento de Sistemas',
             'descricao': 'Curso superior de tecnologia (3 anos).',
             'total_vagas': 3},
            {'nome': 'Gestão da Tecnologia da Informação',
             'descricao': 'Curso superior de tecnologia em GTI.',
             'total_vagas': 2},
        ]
        for d in dados:
            curso, created = Curso.objects.get_or_create(nome=d['nome'], defaults=d)
            self.stdout.write(f'{"Criado" if created else "Já existe"}: {curso.nome}')