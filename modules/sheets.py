import time
import os
import uuid

import gspread
import pandas as pd
import pytz
import streamlit as st
from datetime import datetime


NOME_PLANILHA = "Base_Atendimentos_Engage"

COLUNAS = ["Data", "Hora", "Dia_Semana", "Setor", "Colaborador", "Motivo",
           "Portal", "Nota_Fiscal", "Numero_Pedido", "Motivo_CRM", "Transportadora",
           "Cobranca", "Celular_Cobranca"]


def _obter_data_hora_brasil():
    fuso = pytz.timezone("America/Sao_Paulo")
    return datetime.now(fuso)


def _dia_semana_pt(dt) -> str:
    dias = {0: "Segunda-feira", 1: "Terça-feira", 2: "Quarta-feira",
            3: "Quinta-feira", 4: "Sexta-feira", 5: "Sábado", 6: "Domingo"}
    return dias[dt.weekday()]


def _build_creds():
    if "gcp_service_account" in st.secrets:
        s = st.secrets["gcp_service_account"]
        return {
            "type":                        s["type"],
            "project_id":                  s["project_id"],
            "private_key_id":              s["private_key_id"],
            "private_key":                 s["private_key"].replace(chr(92) + "n", chr(10)),
            "client_email":                s["client_email"],
            "client_id":                   s["client_id"],
            "auth_uri":                    s["auth_uri"],
            "token_uri":                   s["token_uri"],
            "auth_provider_x509_cert_url": s["auth_provider_x509_cert_url"],
            "client_x509_cert_url":        s["client_x509_cert_url"],
        }
    return None


@st.cache_resource(ttl=300, show_spinner=False)
def _conectar() -> gspread.Worksheet | None:
    try:
        creds = _build_creds()
        if creds:
            client = gspread.service_account_from_dict(creds)
        elif os.path.exists("credentials.json"):
            client = gspread.service_account(filename="credentials.json")
        else:
            return None
        return client.open(NOME_PLANILHA).sheet1
    except Exception:
        return None


def salvar_registro(dados: dict) -> bool:
    """Grava uma linha na planilha com 3 tentativas e backoff exponencial."""
    # Guard: rejeita linhas sem campos essenciais para evitar registros em branco
    if not str(dados.get("colaborador", "")).strip():
        return False
    if not str(dados.get("setor", "")).strip():
        return False
    agora = _obter_data_hora_brasil()
    linha = [
        agora.strftime("%d/%m/%Y"),
        agora.strftime("%H:%M:%S"),
        _dia_semana_pt(agora),
        dados.get("setor", ""),
        dados.get("colaborador", ""),
        dados.get("motivo", ""),
        dados.get("portal", ""),
        str(dados.get("nota_fiscal", "")),
        str(dados.get("numero_pedido", "")),
        dados.get("motivo_crm", ""),
        dados.get("transportadora", "-"),
        "TRUE" if dados.get("cobranca") else "FALSE",
        dados.get("celular_cobranca", ""),
    ]
    for tentativa in range(3):
        try:
            sheet = _conectar()
            if sheet is None:
                return False
            sheet.append_row(linha)
            return True
        except Exception:
            if tentativa < 2:
                time.sleep(0.5 * (2 ** tentativa))
    return False


@st.cache_data(ttl=600, show_spinner=False)
def carregar_historico() -> pd.DataFrame:
    """Retorna todos os registros para o Histórico (cache 10 min — dado menos volátil)."""
    sheet = _conectar()
    if sheet is None:
        return pd.DataFrame()
    try:
        registros = sheet.get_all_records()
        if registros:
            return pd.DataFrame(registros)
        return pd.DataFrame(columns=COLUNAS)
    except Exception:
        return pd.DataFrame()


@st.cache_data(ttl=60, show_spinner=False)
def carregar_dados_dashboard() -> pd.DataFrame:
    sheet = _conectar()
    if sheet is None:
        return pd.DataFrame()
    try:
        registros = sheet.get_all_records()
        if registros:
            return pd.DataFrame(registros)
        return pd.DataFrame(columns=COLUNAS)
    except Exception:
        return pd.DataFrame()


# ── Diário de Problemas ───────────────────────────────────────────────────────

COLUNAS_PROBLEMAS = [
    "Data", "Hora", "Colaborador", "Area", "Descricao", "Impacto",
    "Recorrente", "Gravidade", "Causa", "Sugestao", "Referencia",
    "ID", "Status", "Prioridade", "Titulo", "Tags",
    "Responsavel", "ResponsavelTratativa",
    "TipoSolucao", "AcaoTomada", "DocumentoGerado",
]

# Índices 1-based (para gspread) — campos originais e de gestão
_COL_MAP_PROBLEMAS = {
    # Campos originais (editáveis pelo autor enquanto Pendente)
    "Area": 4, "Descricao": 5, "Impacto": 6, "Recorrente": 7,
    "Gravidade": 8, "Causa": 9, "Sugestao": 10, "Referencia": 11,
    # Campos de gestão (editáveis pela gestora)
    "ID": 12, "Status": 13, "Prioridade": 14, "Titulo": 15, "Tags": 16,
    "Responsavel": 17, "ResponsavelTratativa": 18,
    "TipoSolucao": 19, "AcaoTomada": 20, "DocumentoGerado": 21,
}


@st.cache_resource(ttl=300, show_spinner=False)
def _conectar_problemas() -> gspread.Worksheet | None:
    """Conecta à aba 'Problemas_Relatados'. Cria a aba automaticamente se não existir."""
    try:
        creds = _build_creds()
        if creds:
            client = gspread.service_account_from_dict(creds)
        elif os.path.exists("credentials.json"):
            client = gspread.service_account(filename="credentials.json")
        else:
            return None

        planilha = client.open(NOME_PLANILHA)
        try:
            ws = planilha.worksheet("Problemas_Relatados")
            # Migração de schema: atualiza cabeçalho se necessário
            if ws.row_values(1) != COLUNAS_PROBLEMAS:
                ws.update("A1", [COLUNAS_PROBLEMAS])
            return ws
        except gspread.WorksheetNotFound:
            ws = planilha.add_worksheet(title="Problemas_Relatados", rows=1000, cols=25)
            ws.append_row(COLUNAS_PROBLEMAS)
            return ws
    except Exception:
        return None


def salvar_problema(dados: dict) -> bool:
    """Grava uma linha na aba Problemas_Relatados com 3 tentativas e backoff exponencial."""
    agora = _obter_data_hora_brasil()
    linha = [
        agora.strftime("%d/%m/%Y"),
        agora.strftime("%H:%M:%S"),
        dados.get("colaborador", ""),
        dados.get("area", ""),
        dados.get("descricao", ""),
        dados.get("impacto", ""),
        dados.get("recorrente", ""),
        dados.get("gravidade", ""),
        dados.get("causa", ""),
        dados.get("sugestao", ""),
        dados.get("referencia", ""),
        uuid.uuid4().hex[:8].upper(),  # ID único
        "Pendente",   # Status inicial
        "",           # Prioridade
        "",           # Titulo
        "",           # Tags
        "",           # Responsavel
        "",           # ResponsavelTratativa
        "",           # TipoSolucao
        "",           # AcaoTomada
        "",           # DocumentoGerado
    ]
    for tentativa in range(3):
        try:
            sheet = _conectar_problemas()
            if sheet is None:
                return False
            sheet.append_row(linha)
            carregar_problemas.clear()
            return True
        except Exception:
            if tentativa < 2:
                time.sleep(0.5 * (2 ** tentativa))
    return False


def atualizar_problema(problema_id: str, campos: dict) -> bool:
    """Atualiza campos de gestão de um problema pelo seu ID."""
    for tentativa in range(3):
        try:
            sheet = _conectar_problemas()
            if sheet is None:
                return False
            # Localiza linha pelo ID (coluna 11)
            ids = sheet.col_values(_COL_MAP_PROBLEMAS["ID"])
            if problema_id not in ids:
                return False
            row_num = ids.index(problema_id) + 1  # 1-based

            # Monta batch de atualizações
            batch = []
            for campo, valor in campos.items():
                col = _COL_MAP_PROBLEMAS.get(campo)
                if col is not None:
                    col_letra = chr(64 + col)  # colunas 11-19 → K-S (dentro de A-Z)
                    batch.append({"range": f"{col_letra}{row_num}", "values": [[str(valor)]]})

            if batch:
                sheet.batch_update(batch)
            carregar_problemas.clear()
            return True
        except Exception:
            if tentativa < 2:
                time.sleep(0.5 * (2 ** tentativa))
    return False


@st.cache_data(ttl=60, show_spinner=False)
def carregar_problemas() -> pd.DataFrame:
    """Retorna todos os registros de problemas como DataFrame (cache 60s)."""
    sheet = _conectar_problemas()
    if sheet is None:
        return pd.DataFrame()
    try:
        registros = sheet.get_all_records()
        if registros:
            return pd.DataFrame(registros)
        return pd.DataFrame(columns=COLUNAS_PROBLEMAS)
    except Exception:
        return pd.DataFrame()


# ── Acompanhamento de Tratativas ──────────────────────────────────────────────

COLUNAS_ACOMPANHAMENTO = [
    "Data", "Hora", "ProblemID", "ProblemTitulo", "Colaborador", "Atualizacao",
]


@st.cache_resource(ttl=300, show_spinner=False)
def _conectar_acompanhamento() -> gspread.Worksheet | None:
    """Conecta à aba 'Acompanhamento_Problemas'. Cria automaticamente se não existir."""
    try:
        creds = _build_creds()
        if creds:
            client = gspread.service_account_from_dict(creds)
        elif os.path.exists("credentials.json"):
            client = gspread.service_account(filename="credentials.json")
        else:
            return None

        planilha = client.open(NOME_PLANILHA)
        try:
            ws = planilha.worksheet("Acompanhamento_Problemas")
            if ws.row_values(1) != COLUNAS_ACOMPANHAMENTO:
                ws.update("A1", [COLUNAS_ACOMPANHAMENTO])
            return ws
        except gspread.WorksheetNotFound:
            ws = planilha.add_worksheet(title="Acompanhamento_Problemas", rows=1000, cols=10)
            ws.append_row(COLUNAS_ACOMPANHAMENTO)
            return ws
    except Exception:
        return None


def salvar_acompanhamento(dados: dict) -> bool:
    """Grava uma atualização de acompanhamento com 3 tentativas e backoff exponencial."""
    if not str(dados.get("atualizacao", "")).strip():
        return False
    if not str(dados.get("colaborador", "")).strip():
        return False

    agora = _obter_data_hora_brasil()
    linha = [
        agora.strftime("%d/%m/%Y"),
        agora.strftime("%H:%M:%S"),
        dados.get("problem_id", ""),
        dados.get("problem_titulo", ""),
        dados.get("colaborador", ""),
        dados.get("atualizacao", ""),
    ]
    for tentativa in range(3):
        try:
            sheet = _conectar_acompanhamento()
            if sheet is None:
                return False
            sheet.append_row(linha)
            carregar_acompanhamentos.clear()
            return True
        except Exception:
            if tentativa < 2:
                time.sleep(0.5 * (2 ** tentativa))
    return False


@st.cache_data(ttl=60, show_spinner=False)
def carregar_acompanhamentos() -> pd.DataFrame:
    """Retorna todos os registros de acompanhamento como DataFrame (cache 60s)."""
    sheet = _conectar_acompanhamento()
    if sheet is None:
        return pd.DataFrame()
    try:
        registros = sheet.get_all_records()
        if registros:
            return pd.DataFrame(registros)
        return pd.DataFrame(columns=COLUNAS_ACOMPANHAMENTO)
    except Exception:
        return pd.DataFrame()
