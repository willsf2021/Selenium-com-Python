from django.db import models

class Curso(models.Model):
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True)
    total_vagas = models.PositiveIntegerField(default=10)

    def __str__(self):
        return self.nome

    @property
    def vagas_ocupadas(self):
        return self.candidatos.filter(status='aprovado').count()

    @property
    def vagas_disponiveis(self):
        return max(0, self.total_vagas - self.vagas_ocupadas)


class Candidato(models.Model):
    TIPO_COTISTA = 1
    TIPO_AMPLA = 2
    TIPO_CHOICES = [
        (TIPO_COTISTA, 'Cotista'),
        (TIPO_AMPLA, 'Ampla Concorrência'),
    ]
    STATUS_CHOICES = [
        ('espera', 'Em Espera'),
        ('aprovado', 'Aprovado'),
    ]

    curso = models.ForeignKey(Curso, on_delete=models.CASCADE, related_name='candidatos')
    nome = models.CharField(max_length=200)
    email = models.EmailField()
    cpf = models.CharField(max_length=14)
    tipo = models.IntegerField(choices=TIPO_CHOICES, default=TIPO_AMPLA)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='espera')
    data_inscricao = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [['curso', 'cpf']]
        ordering = ['tipo', 'data_inscricao']  # cotista (1) antes de ampla (2)

    def __str__(self):
        return f"{self.nome} ({self.get_tipo_display()})"