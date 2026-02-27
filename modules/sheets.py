import time
import os

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
    "Data", "Hora", "Colaborador", "Area", "Descricao",
    "Recorrente", "Gravidade", "Causa", "Sugestao", "Referencia",
]


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
            return planilha.worksheet("Problemas_Relatados")
        except gspread.WorksheetNotFound:
            ws = planilha.add_worksheet(title="Problemas_Relatados", rows=1000, cols=20)
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
        dados.get("recorrente", ""),
        dados.get("gravidade", ""),
        dados.get("causa", ""),
        dados.get("sugestao", ""),
        dados.get("referencia", ""),
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
