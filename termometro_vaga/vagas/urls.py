from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_cursos, name='lista_cursos'),
    path('curso/<int:curso_id>/', views.detalhe_curso, name='detalhe_curso'),
    path('curso/<int:curso_id>/liberar/', views.liberar_vaga, name='liberar_vaga'),
    path('posicao/', views.consultar_posicao, name='consultar_posicao'),
]