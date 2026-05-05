"""
==============================================================================
 TESTES SELENIUM - Sistema "Termometro de Vaga"
==============================================================================
 Apresentacao: Python + Selenium nos Quadrantes do Teste Agil
 Wilson Junior - FATEC

 ** MODO DEMO ATIVADO **
 - Digitacao caractere por caractere (visualmente perceptivel)
 - Delays entre acoes para a plateia acompanhar
 - Destaque visual nos elementos antes de cada clique (borda vermelha)
 - Pausa de 3s antes de fechar o navegador

 Para rodar em modo CI (rapido, headless), defina DEMO_MODE = False abaixo.

 PRE-REQUISITOS:
   1. Servidor Django rodando:    python manage.py runserver
   2. Banco populado:              python manage.py seed
   3. (Recomendado) Reset entre demos:
      python manage.py flush --no-input && python manage.py seed
   4. pip install selenium pytest

 EXECUCAO:
   pytest tests_selenium.py -v -s     # -s mostra os prints da narracao
   pytest tests_selenium.py::test_prioridade_cotista_funciona -v -s
==============================================================================
"""

import time
import random
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options


# ----------- CONFIGURACAO -----------
BASE_URL = "http://127.0.0.1:8000"
CURSO_ID = 1

# Modo DEMO: lento e visual. Modo CI: rapido e headless.
DEMO_MODE = True

# Delays (em segundos) - so usados quando DEMO_MODE = True
DELAY_DIGITACAO = 0.07          # entre cada caractere digitado
DELAY_ENTRE_ACOES = 0.6         # entre acoes (clicar, preencher, etc)
DELAY_ANTES_ASSERT = 1.2        # pausa antes de validar resultado
DELAY_FINAL = 3.0               # tempo pra plateia ver o resultado final
DELAY_ANTES_CLIQUE = 0.4        # tempo do destaque visual antes de clicar

WAIT_TIMEOUT = 8                # timeout das esperas inteligentes


# ----------- HELPERS DE DEMO -----------
def narrar(mensagem):
    """Imprime narracao no terminal pra acompanhar a demo."""
    if DEMO_MODE:
        print(f"\n  >> {mensagem}")


def pausar(segundos=None):
    """Pausa configuravel - so atua em modo demo."""
    if DEMO_MODE:
        time.sleep(segundos if segundos is not None else DELAY_ENTRE_ACOES)


def destacar(driver, elemento, cor="red"):
    """Destaca um elemento com borda colorida e leve glow.
    Truque classico de Selenium pra demos: a plateia ve onde o robo vai agir."""
    if DEMO_MODE:
        driver.execute_script(
            "arguments[0].style.border='3px solid " + cor + "';"
            "arguments[0].style.boxShadow='0 0 12px " + cor + "';"
            "arguments[0].style.transition='all 0.2s';",
            elemento
        )
        time.sleep(DELAY_ANTES_CLIQUE)


def remover_destaque(driver, elemento):
    """Remove o destaque depois da acao."""
    if DEMO_MODE:
        driver.execute_script(
            "arguments[0].style.border=''; arguments[0].style.boxShadow='';",
            elemento
        )


def digitar_devagar(elemento, texto):
    """Digita caractere por caractere - aparece como humano teclando."""
    if DEMO_MODE:
        for c in texto:
            elemento.send_keys(c)
            time.sleep(DELAY_DIGITACAO)
    else:
        elemento.send_keys(texto)


def clicar_com_destaque(driver, elemento):
    """Destaca, clica e remove o destaque - sequencia visual completa."""
    destacar(driver, elemento)
    elemento.click()


# ----------- HELPERS GERAIS -----------
def gerar_cpf():
    """11 digitos aleatorios. Cada execucao usa CPFs novos."""
    return ''.join(str(random.randint(0, 9)) for _ in range(11))


@pytest.fixture
def driver():
    """Cria e destroi o navegador a cada teste."""
    options = Options()
    if not DEMO_MODE:
        options.add_argument("--headless=new")
    options.add_argument("--window-size=1280,800")
    options.add_argument("--disable-notifications")
    drv = webdriver.Chrome(options=options)
    drv.implicitly_wait(2)

    yield drv

    if DEMO_MODE:
        narrar(f"Pausa final de {DELAY_FINAL}s pra apreciar o resultado...")
        time.sleep(DELAY_FINAL)
    drv.quit()


def esperar(driver, seletor):
    """Espera inteligente: aguarda elemento existir.
    Esse padrao e o que separa teste robusto de teste flaky."""
    return WebDriverWait(driver, WAIT_TIMEOUT).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, seletor))
    )


def inscrever(driver, nome, email, cpf, tipo):
    """Preenche e submete o formulario de inscricao.
    tipo=1 e COTISTA (prioridade), tipo=2 e AMPLA CONCORRENCIA."""
    narrar(f"Abrindo pagina do curso e inscrevendo {nome} ({'Cotista' if tipo == 1 else 'Ampla'})")
    driver.get(f"{BASE_URL}/curso/{CURSO_ID}/")
    pausar()

    campo_nome = driver.find_element(By.NAME, "nome")
    destacar(driver, campo_nome)
    digitar_devagar(campo_nome, nome)
    remover_destaque(driver, campo_nome)
    pausar()

    campo_email = driver.find_element(By.NAME, "email")
    destacar(driver, campo_email)
    digitar_devagar(campo_email, email)
    remover_destaque(driver, campo_email)
    pausar()

    campo_cpf = driver.find_element(By.NAME, "cpf")
    destacar(driver, campo_cpf)
    digitar_devagar(campo_cpf, cpf)
    remover_destaque(driver, campo_cpf)
    pausar()

    campo_tipo = driver.find_element(By.NAME, "tipo")
    destacar(driver, campo_tipo)
    Select(campo_tipo).select_by_value(str(tipo))
    remover_destaque(driver, campo_tipo)
    pausar()

    botao = driver.find_element(By.CSS_SELECTOR, '[data-testid="btn-inscrever"]')
    narrar("Submetendo o formulario...")
    clicar_com_destaque(driver, botao)


# ==============================================================
# CENARIO 1 - HAPPY PATH
# ==============================================================
def test_inscricao_com_sucesso(driver):
    """Historia: 'Como candidato, quero me inscrever no curso e ver
    confirmacao para saber que minha vaga foi registrada.'"""
    narrar("=== CENARIO 1: Inscricao com sucesso ===")
    nome = f"Maria_{random.randint(1000, 9999)}"
    inscrever(driver, nome, "maria@teste.com", gerar_cpf(), 2)

    pausar(DELAY_ANTES_ASSERT)
    msg = esperar(driver, '[data-testid="msg-success"]')
    narrar(f"Mensagem recebida: {msg.text}")
    assert "sucesso" in msg.text.lower()

    fila = driver.find_element(By.CSS_SELECTOR, '[data-testid="lista-fila"]')
    assert nome in fila.text
    narrar(f"OK - {nome} aparece na fila")


# ==============================================================
# CENARIO 2 - REGRA DE NEGOCIO (CPF DUPLICADO)
# ==============================================================
def test_cpf_duplicado_e_bloqueado(driver):
    """Regra: mesmo CPF nao pode se inscrever 2x no mesmo curso."""
    narrar("=== CENARIO 2: CPF duplicado e bloqueado ===")
    cpf = gerar_cpf()

    narrar("Primeira inscricao (deve passar)...")
    inscrever(driver, "Joao Original", "joao@teste.com", cpf, 2)
    esperar(driver, '[data-testid="msg-success"]')
    pausar(DELAY_ANTES_ASSERT)

    narrar(f"Tentando inscrever de novo com o MESMO CPF {cpf} (deve falhar)...")
    inscrever(driver, "Joao Tentativa 2", "joao2@teste.com", cpf, 2)

    pausar(DELAY_ANTES_ASSERT)
    msg = esperar(driver, '[data-testid="msg-error"]')
    narrar(f"Mensagem de erro recebida: {msg.text}")
    assert "ja esta inscrito" in msg.text.lower() or "já está inscrito" in msg.text.lower()


# ==============================================================
# CENARIO 3 - VALIDACAO DE FORMULARIO
# ==============================================================
def test_cpf_invalido_e_rejeitado(driver):
    """Validacao no clean_cpf: precisa ter 11 digitos."""
    narrar("=== CENARIO 3: CPF invalido (apenas 3 digitos) deve ser rejeitado ===")
    inscrever(driver, "Fulano", "fulano@teste.com", "123", 2)

    pausar(DELAY_ANTES_ASSERT)
    erros = driver.find_elements(By.CLASS_NAME, "errorlist")
    assert len(erros) > 0
    texto_erros = " ".join(e.text for e in erros)
    narrar(f"Erro de validacao recebido: {texto_erros}")
    assert "11" in texto_erros or "CPF" in texto_erros.upper()


# ==============================================================
# CENARIO 4 - O TESTE-ESTRELA: PRIORIDADE COTISTA
# ==============================================================
def test_prioridade_cotista_funciona(driver):
    """O teste-estrela da apresentacao.

    Historia: 'Cotistas tem prioridade sobre ampla concorrencia,
    mesmo se inscritos depois.'
    """
    narrar("=== CENARIO 4 (ESTRELA): Prioridade do Cotista ===")
    nome_ampla = f"Ampla_{random.randint(10000, 99999)}"
    nome_cotista = f"Cotista_{random.randint(10000, 99999)}"

    narrar("Passo 1: AMPLA se inscreve PRIMEIRO")
    inscrever(driver, nome_ampla, "ampla@teste.com", gerar_cpf(), 2)
    esperar(driver, '[data-testid="msg-success"]')
    pausar(DELAY_ANTES_ASSERT)

    narrar("Passo 2: COTISTA se inscreve DEPOIS")
    inscrever(driver, nome_cotista, "cotista@teste.com", gerar_cpf(), 1)
    esperar(driver, '[data-testid="msg-success"]')
    pausar(DELAY_ANTES_ASSERT)

    narrar("Verificacao 1: na fila, o cotista deve vir ANTES (mesmo chegando depois)...")
    nomes_fila = [el.text for el in driver.find_elements(
        By.CSS_SELECTOR, '[data-testid="fila-nome"]')]
    narrar(f"Ordem atual da fila: {nomes_fila}")
    assert nome_cotista in nomes_fila and nome_ampla in nomes_fila
    assert nomes_fila.index(nome_cotista) < nomes_fila.index(nome_ampla)
    narrar("OK - cotista esta antes do ampla na fila")
    pausar(DELAY_ANTES_ASSERT)

    narrar("Passo 3: liberar 1 vaga e verificar quem foi aprovado")
    botao_liberar = driver.find_element(By.CSS_SELECTOR, '[data-testid="btn-liberar-vaga"]')
    clicar_com_destaque(driver, botao_liberar)
    esperar(driver, '[data-testid="msg-success"]')
    pausar(DELAY_ANTES_ASSERT)

    aprovados = [el.text for el in driver.find_elements(
        By.CSS_SELECTOR, '[data-testid="aprovado-nome"]')]
    narrar(f"Aprovados: {aprovados}")
    assert nome_cotista in aprovados, f"COTISTA deveria estar aprovado. Aprovados: {aprovados}"
    assert nome_ampla not in aprovados, f"AMPLA NAO deveria estar aprovado ainda. Aprovados: {aprovados}"
    narrar("OK - regra de prioridade funcionou: cotista aprovado, ampla aguardando")


# ==============================================================
# CENARIO 5 - CONSULTA DE POSICAO
# ==============================================================
def test_consultar_posicao_na_fila(driver):
    """Historia: 'Como candidato, quero consultar minha posicao na fila
    informando meu CPF.'"""
    narrar("=== CENARIO 5: Consulta de posicao na fila ===")
    cpf = gerar_cpf()
    nome = f"Consultor_{random.randint(1000, 9999)}"

    narrar("Primeiro: inscrever um candidato")
    inscrever(driver, nome, "consulta@teste.com", cpf, 2)
    esperar(driver, '[data-testid="msg-success"]')
    pausar(DELAY_ANTES_ASSERT)

    narrar(f"Agora consultar a posicao usando o CPF {cpf}")
    driver.get(f"{BASE_URL}/posicao/")
    pausar()

    campo_cpf = driver.find_element(By.CSS_SELECTOR, '[data-testid="input-cpf"]')
    destacar(driver, campo_cpf)
    digitar_devagar(campo_cpf, cpf)
    remover_destaque(driver, campo_cpf)
    pausar()

    botao = driver.find_element(By.CSS_SELECTOR, '[data-testid="btn-consultar"]')
    clicar_com_destaque(driver, botao)

    pausar(DELAY_ANTES_ASSERT)
    resultado = esperar(driver, '[data-testid="resultado-nome"]')
    narrar(f"Resultado encontrado: {resultado.text}")
    assert nome in resultado.text

    status = driver.find_element(By.CSS_SELECTOR, '[data-testid="status"]')
    narrar(f"Status: {status.text}")
    assert "espera" in status.text.lower() or "aprovado" in status.text.lower()


# ==============================================================
# DICAS DE AJUSTE PARA A APRESENTACAO
# ==============================================================
# Se a demo estiver MUITO lenta, reduza:
#   - DELAY_DIGITACAO de 0.07 para 0.04
#   - DELAY_ENTRE_ACOES de 0.6 para 0.4
#
# Se quiser MAIS pausa pra explicar cada etapa:
#   - aumente DELAY_ANTES_ASSERT de 1.2 para 2.0
#   - aumente DELAY_FINAL de 3.0 para 5.0
#
# Se quiser apenas o teste-estrela rodando lento (resto rapido):
#   - mantenha DEMO_MODE = True
#   - rode: pytest tests_selenium.py::test_prioridade_cotista_funciona -v -s