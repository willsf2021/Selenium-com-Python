from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Curso, Candidato
from .forms import InscricaoForm

def lista_cursos(request):
    cursos = Curso.objects.all()
    return render(request, 'vagas/lista_cursos.html', {'cursos': cursos})

def detalhe_curso(request, curso_id):
    curso = get_object_or_404(Curso, pk=curso_id)

    if request.method == 'POST':
        form = InscricaoForm(request.POST)
        if form.is_valid():
            cpf = form.cleaned_data['cpf']
            if Candidato.objects.filter(curso=curso, cpf=cpf).exists():
                messages.error(request, 'Este CPF já está inscrito neste curso.')
            else:
                candidato = form.save(commit=False)
                candidato.curso = curso
                candidato.save()
                messages.success(request, f'Inscrição de {candidato.nome} realizada com sucesso!')
                return redirect('detalhe_curso', curso_id=curso.id)
    else:
        form = InscricaoForm()

    fila = curso.candidatos.filter(status='espera').order_by('tipo', 'data_inscricao')
    aprovados = curso.candidatos.filter(status='aprovado').order_by('-data_inscricao')

    return render(request, 'vagas/detalhe_curso.html', {
        'curso': curso, 'form': form, 'fila': fila, 'aprovados': aprovados,
    })

def liberar_vaga(request, curso_id):
    curso = get_object_or_404(Curso, pk=curso_id)
    if request.method == 'POST':
        if curso.vagas_disponiveis > 0:
            proximo = curso.candidatos.filter(status='espera').order_by('tipo', 'data_inscricao').first()
            if proximo:
                proximo.status = 'aprovado'
                proximo.save()
                messages.success(request, f'{proximo.nome} foi aprovado(a)!')
            else:
                messages.warning(request, 'Não há candidatos na fila.')
        else:
            messages.error(request, 'Não há vagas disponíveis.')
    return redirect('detalhe_curso', curso_id=curso.id)

def consultar_posicao(request):
    candidato = None
    posicao = None
    consultou = False
    if request.method == 'POST':
        consultou = True
        cpf = request.POST.get('cpf', '').replace('.', '').replace('-', '').strip()
        candidatos = Candidato.objects.filter(cpf=cpf)
        if candidatos.exists():
            candidato = candidatos.first()
            if candidato.status == 'espera':
                fila = list(candidato.curso.candidatos.filter(status='espera').order_by('tipo', 'data_inscricao'))
                for i, c in enumerate(fila, 1):
                    if c.id == candidato.id:
                        posicao = i
                        break
    return render(request, 'vagas/posicao.html', {
        'candidato': candidato, 'posicao': posicao, 'consultou': consultou,
    })