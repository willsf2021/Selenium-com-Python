"""
==============================================================================
 TESTES SELENIUM - Sistema "Termômetro de Vaga"
==============================================================================
 Apresentacao: Python + Selenium nos Quadrantes do Teste Agil
 Wilson Junior - FATEC

 CLASSIFICACAO NOS QUADRANTES (Crispin & Gregory):
   - Q2 principal: testes funcionais voltados ao negocio que APOIAM a equipe
   - Cada teste valida uma "condicao de satisfacao do negocio"
   - Selenium toca tambem Q3 (setup p/ exploratorio) e Q4 (orquestracao de carga)

 PRE-REQUISITOS:
   1. Servidor Django rodando:    python manage.py runserver
   2. Banco populado:              python manage.py seed
   3. (Opcional) Reset entre demos: python manage.py flush --no-input && python manage.py seed
   4. Selenium 4.6+ (ja vem com Selenium Manager - baixa o ChromeDriver sozinho)
      pip install selenium pytest

 EXECUCAO:
   pytest tests_selenium.py -v                    # roda todos
   pytest tests_selenium.py::test_prioridade_cotista_funciona -v   # so o teste-estrela
==============================================================================
"""

import random
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options


# ----------- CONFIGURACAO -----------
BASE_URL = "http://127.0.0.1:8000"
CURSO_ID = 1            # primeiro curso criado pelo seed
HEADLESS = False        # True = sem janela (mais rapido); False = visual (melhor pra demo)
WAIT_TIMEOUT = 8        # segundos maximos pra esperas inteligentes


# ----------- HELPERS -----------
def gerar_cpf():
    """Gera 11 digitos aleatorios. Cada execucao do teste usa CPFs novos -
    evita conflito com a constraint UNIQUE do modelo."""
    return ''.join(str(random.randint(0, 9)) for _ in range(11))


@pytest.fixture
def driver():
    """Cria e destroi o navegador a cada teste. Isolamento garantido."""
    options = Options()
    if HEADLESS:
        options.add_argument("--headless=new")
    options.add_argument("--window-size=1280,800")
    options.add_argument("--disable-notifications")
    drv = webdriver.Chrome(options=options)
    drv.implicitly_wait(2)
    yield drv
    drv.quit()


def esperar(driver, seletor):
    """Espera inteligente: aguarda o elemento existir ate WAIT_TIMEOUT segundos.
    Esse padrao e o que separa um teste robusto de um teste flaky."""
    return WebDriverWait(driver, WAIT_TIMEOUT).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, seletor))
    )


def inscrever(driver, nome, email, cpf, tipo):
    """Helper de Page Object simplificado: preenche o formulario de inscricao.
    tipo=1 e COTISTA (prioridade), tipo=2 e AMPLA CONCORRENCIA."""
    driver.get(f"{BASE_URL}/curso/{CURSO_ID}/")
    driver.find_element(By.NAME, "nome").send_keys(nome)
    driver.find_element(By.NAME, "email").send_keys(email)
    driver.find_element(By.NAME, "cpf").send_keys(cpf)
    Select(driver.find_element(By.NAME, "tipo")).select_by_value(str(tipo))
    driver.find_element(By.CSS_SELECTOR, '[data-testid="btn-inscrever"]').click()


# ==============================================================
# CENARIO 1 - HAPPY PATH (story test do Q2)
# ==============================================================
def test_inscricao_com_sucesso(driver):
    """Historia: 'Como candidato, quero me inscrever no curso e ver
    confirmacao para saber que minha vaga foi registrada.'"""
    nome = f"Maria_{random.randint(1000, 9999)}"
    inscrever(driver, nome, "maria@teste.com", gerar_cpf(), 2)

    msg = esperar(driver, '[data-testid="msg-success"]')
    assert "sucesso" in msg.text.lower()

    fila = driver.find_element(By.CSS_SELECTOR, '[data-testid="lista-fila"]')
    assert nome in fila.text, f"Esperava {nome} na fila, encontrei: {fila.text[:200]}"


# ==============================================================
# CENARIO 2 - REGRA DE NEGOCIO (CPF DUPLICADO)
# ==============================================================
def test_cpf_duplicado_e_bloqueado(driver):
    """Regra: mesmo CPF nao pode se inscrever 2x no mesmo curso.
    Implementada via unique_together no model + check explicito na view."""
    cpf = gerar_cpf()

    # 1a inscricao: passa
    inscrever(driver, "Joao Original", "joao@teste.com", cpf, 2)
    esperar(driver, '[data-testid="msg-success"]')

    # 2a inscricao (mesmo CPF): falha
    inscrever(driver, "Joao Tentativa 2", "joao2@teste.com", cpf, 2)
    msg = esperar(driver, '[data-testid="msg-error"]')
    assert "ja esta inscrito" in msg.text.lower() or "já está inscrito" in msg.text.lower()


# ==============================================================
# CENARIO 3 - VALIDACAO DE FORMULARIO
# ==============================================================
def test_cpf_invalido_e_rejeitado(driver):
    """Validacao no clean_cpf do form: precisa ter 11 digitos."""
    inscrever(driver, "Fulano", "fulano@teste.com", "123", 2)

    erros = driver.find_elements(By.CLASS_NAME, "errorlist")
    assert len(erros) > 0, "Esperava pelo menos um erro de validacao"
    texto_erros = " ".join(e.text for e in erros)
    assert "11" in texto_erros or "CPF" in texto_erros.upper()


# ==============================================================
# CENARIO 4 - O TESTE-ESTRELA: PRIORIDADE COTISTA
# ==============================================================
def test_prioridade_cotista_funciona(driver):
    """O teste mais importante da apresentacao.

    Historia: 'Como instituicao, candidatos cotistas devem ter prioridade
    sobre ampla concorrencia, mesmo se inscritos depois.'

    Cenario:
      1. AMPLA se inscreve primeiro
      2. COTISTA se inscreve depois
      3. Ao liberar 1 vaga, o COTISTA deve ser aprovado (nao o ampla)
    """
    nome_ampla = f"Ampla_{random.randint(10000, 99999)}"
    nome_cotista = f"Cotista_{random.randint(10000, 99999)}"

    # Passo 1: AMPLA primeiro
    inscrever(driver, nome_ampla, "ampla@teste.com", gerar_cpf(), 2)
    esperar(driver, '[data-testid="msg-success"]')

    # Passo 2: COTISTA depois
    inscrever(driver, nome_cotista, "cotista@teste.com", gerar_cpf(), 1)
    esperar(driver, '[data-testid="msg-success"]')

    # Verificacao intermediaria: na fila, cotista vem ANTES (apesar de ter chegado depois)
    nomes_fila = [el.text for el in driver.find_elements(
        By.CSS_SELECTOR, '[data-testid="fila-nome"]')]
    assert nome_cotista in nomes_fila and nome_ampla in nomes_fila
    assert nomes_fila.index(nome_cotista) < nomes_fila.index(nome_ampla), \
        f"Cotista deveria vir antes do Ampla. Ordem atual: {nomes_fila}"

    # Passo 3: liberar uma vaga e verificar quem foi aprovado
    driver.find_element(By.CSS_SELECTOR, '[data-testid="btn-liberar-vaga"]').click()
    esperar(driver, '[data-testid="msg-success"]')

    aprovados = [el.text for el in driver.find_elements(
        By.CSS_SELECTOR, '[data-testid="aprovado-nome"]')]
    assert nome_cotista in aprovados, \
        f"COTISTA deveria estar aprovado. Aprovados: {aprovados}"
    assert nome_ampla not in aprovados, \
        f"AMPLA NAO deveria estar aprovado ainda. Aprovados: {aprovados}"


# ==============================================================
# CENARIO 5 - CONSULTA DE POSICAO (fluxo de usuario externo)
# ==============================================================
def test_consultar_posicao_na_fila(driver):
    """Historia: 'Como candidato, quero consultar minha posicao na fila
    informando meu CPF para acompanhar minha situacao.'"""
    cpf = gerar_cpf()
    nome = f"Consultor_{random.randint(1000, 9999)}"

    inscrever(driver, nome, "consulta@teste.com", cpf, 2)
    esperar(driver, '[data-testid="msg-success"]')

    driver.get(f"{BASE_URL}/posicao/")
    driver.find_element(By.CSS_SELECTOR, '[data-testid="input-cpf"]').send_keys(cpf)
    driver.find_element(By.CSS_SELECTOR, '[data-testid="btn-consultar"]').click()

    resultado = esperar(driver, '[data-testid="resultado-nome"]')
    assert nome in resultado.text

    status = driver.find_element(By.CSS_SELECTOR, '[data-testid="status"]')
    assert "espera" in status.text.lower() or "aprovado" in status.text.lower()


# ==============================================================
# BONUS - DEMONSTRACAO DE TESTE FLAKY (mostrar e depois corrigir)
# ==============================================================
# Descomente este teste durante a apresentacao para mostrar o problema
# de timing e como o WebDriverWait resolve.
#
# def test_VERSAO_FLAKY_sem_wait(driver):
#     inscrever(driver, "Flaky", "flaky@teste.com", gerar_cpf(), 2)
#     # SEM espera inteligente - as vezes passa, as vezes falha
#     msg = driver.find_element(By.CSS_SELECTOR, '[data-testid="msg-success"]')
#     assert "sucesso" in msg.text.lower()