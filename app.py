import streamlit as st
import pandas as pd
import plotly.express as px
import os
import pytz
import json
import gspread
from datetime import datetime
import streamlit.components.v1 as components

# ==========================================
#      1. CONFIGURAÇÃO INICIAL
# ==========================================
st.set_page_config(page_title="Sistema Integrado Engage", page_icon="🚀", layout="wide")

# Estilização CSS para melhor visualização
st.markdown("""
    <style>
    .preview-box {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #10b981;
        font-family: 'monospace';
        white-space: pre-wrap;
        margin-bottom: 20px;
    }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #10b981; color: white; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
#      2. MENU LATERAL
# ==========================================
if os.path.exists("logo.png"):
    st.sidebar.image("logo.png", width=180)

st.sidebar.caption("MENU PRINCIPAL")
pagina_escolhida = st.sidebar.radio(
    "Navegação:", 
    ("Pendências Logísticas", "SAC / Atendimento", "📊 Dashboard Gerencial"), 
    label_visibility="collapsed"
)
st.sidebar.markdown("---")

# ==========================================
#      3. FUNÇÕES E CONEXÕES
# ==========================================
NOME_PLANILHA_GOOGLE = "Base_Atendimentos_Engage" 

def conectar_google_sheets():
    try:
        if "gcp_service_account" in st.secrets:
            secrets = st.secrets["gcp_service_account"]
            creds_dict = {
                "type": secrets["type"],
                "project_id": secrets["project_id"],
                "private_key_id": secrets["private_key_id"],
                "private_key": secrets["private_key"].replace("\\n", "\n"), 
                "client_email": secrets["client_email"],
                "client_id": secrets["client_id"],
                "auth_uri": secrets["auth_uri"],
                "token_uri": secrets["token_uri"],
                "auth_provider_x509_cert_url": secrets["auth_provider_x509_cert_url"],
                "client_x509_cert_url": secrets["client_x509_cert_url"]
            }
            client = gspread.service_account_from_dict(creds_dict)
            sheet = client.open(NOME_PLANILHA_GOOGLE).sheet1
            return sheet
        elif os.path.exists("credentials.json"):
            client = gspread.service_account(filename="credentials.json")
            sheet = client.open(NOME_PLANILHA_GOOGLE).sheet1
            return sheet
        else:
            st.error("🚨 Nenhuma credencial encontrada.")
            return None
    except Exception as e:
        st.error(f"Erro de Conexão: {e}")
        return None

def carregar_dados():
    sheet = conectar_google_sheets()
    if sheet:
        try:
            dados = sheet.get_all_records()
            return pd.DataFrame(dados) if dados else pd.DataFrame(columns=["Data", "Hora", "Dia_Semana", "Setor", "Colaborador", "Motivo", "Portal", "Nota_Fiscal", "Numero_Pedido", "Motivo_CRM", "Transportadora"])
        except Exception as e:
            st.error(f"Erro ao ler dados: {e}")
    return pd.DataFrame()

def obter_data_hora_brasil():
    return datetime.now(pytz.timezone('America/Sao_Paulo'))

def obter_dia_semana_pt(dt):
    dias = {0: "Segunda-feira", 1: "Terça-feira", 2: "Quarta-feira", 3: "Quinta-feira", 4: "Sexta-feira", 5: "Sábado", 6: "Domingo"}
    return dias[dt.weekday()]

def salvar_registro(setor, colaborador, motivo, portal, nf, numero_pedido, motivo_crm, transportadora="-"):
    sheet = conectar_google_sheets()
    if sheet:
        agora = obter_data_hora_brasil()
        nova_linha = [agora.strftime("%d/%m/%Y"), agora.strftime("%H:%M:%S"), obter_dia_semana_pt(agora), setor, colaborador, motivo, portal, str(nf), str(numero_pedido), motivo_crm, transportadora]
        try:
            sheet.append_row(nova_linha)
            return True
        except Exception as e:
            st.error(f"Erro ao gravar: {e}")
    return False

def copiar_para_clipboard(texto):
    texto_json = json.dumps(texto)
    js = f"""<script>
    const text = {texto_json};
    const textArea = document.createElement("textarea");
    textArea.value = text;
    document.body.appendChild(textArea);
    textArea.select();
    document.execCommand('copy');
    document.body.removeChild(textArea);
    </script>"""
    components.html(js, height=0, width=0)

# ==========================================
#      4. DADOS E LISTAS
# ==========================================
colaboradores_pendencias = sorted(["Ana", "Mariana", "Gabriela", "Layra", "Maria Eduarda", "Akisia", "Marcelly", "Camilla", "Michelle"])
colaboradores_sac = sorted(["Ana Carolina", "Ana Victoria", "Eliane", "Cassia", "Juliana", "Tamara", "Rafaela", "Telliane", "Isadora", "Lorrayne", "Leticia", "Julia", "Sara", "Cauê", "Larissa", "Marcelly", "Camilla", "Akisia", "Mariana", "Gabriela", "Thais", "Maria Clara", "Izabel", "Jessica", "Marina"])
lista_transportadoras = sorted(["4ELOS", "ATUAL", "BRASIL WEB", "FAVORITA", "FRONTLOG", "GENEROSO", "JADLOG", "LOGAN", "MMA", "PAJUÇARA", "PATRUS", "REBOUÇAS", "REDE SUL", "RIO EXPRESS", "TJB", "TOTAL", "TRILOG"])
lista_portais = sorted(["ALIEXPRESS", "AMAZON - EXTREMA", "AMAZON | ENGAGE LOG", "AMAZON DBA", "AMERICANAS - EXTREMA", "B2W", "BRADESCO SHOP", "CARREFOUR", "CARREFOUR OUTLET", "CNOVA", "CNOVA - EXTREMA", "FAST SHOP", "KABUM", "LEROY - EXTREMA", "MADEIRA MADEIRA", "MAGALU - EXTREMA", "MAGALU ELETRO", "MAGALU INFO", "MARTINS", "MEGA B2B", "MELI OUTLET", "MERCADO LIVRE", "MERCADO LIVRE - EXTREMA", "O MAGAZINE", "PADRÃO", "SHOPEE", "SKYHUB", "TIKTOK", "WAPSTORE - ENGAGE", "WEBCONTINENTAL", "WINECOM - LOJA INTEGRADA", "ZEMA", "SHEIN"])
lista_motivo_crm = sorted(["ACAREAÇÃO", "ACORDO CLIENTE", "ALTERAÇÃO DE NOTA FISCAL", "AREA DE RISCO", "AREA NÃO ATENDIDA", "ARREPENDIMENTO", "ARREPENDIMENTO - DEVOLUÇÃO AMAZON", "ARREPENDIMENTO POR QUALIDADE DO PRODUTO", "ATRASO NA ENTREGA", "ATRASO NA EXPEDIÇÃO", "AUSENTE", "AVARIA", "CANCELAMENTO FORÇADO PELO PORTAL", "CASO JURIDÍCO", "CORREÇÃO DE ENDEREÇO", "DEFEITO", "DESCONHECIDO", "DESCONTO", "DEVOLUÇÃO SEM INFORMAÇÃO", "ENDEREÇO NÃO LOCALIZADO", "ENTREGA C/ AVARIA FORÇADA", "ENTREGUE E CANCELADO", "ERRO DE CADASTRO", "ERRO DE EXPEDIÇÃO", "ERRO DE INTEGRAÇÃO DE FATURAMENTO", "ESTOQUE FALTANTE", "EXTRAVIO", "FALTA DE ETIQUETA ENVIAS", "INSUCESSO NA ENTREGA", "ITEM FALTANTE", "MERCADORIA RETIDA", "MUDOU-SE", "NOTA RETIDA", "PAGAMENTO/REEMBOLSO", "RECOBRANÇA DE CLIENTE", "RECUSA", "RETENÇÃO", "SEM ABERTURA DE CRM", "SEM RASTREIO", "SUSPEITA DE FRAUDE", "TROCA DE ETIQUETA", "ZONA RURAL"])

# --- Modelos de Mensagem ---
modelos_pendencias = {
    "ATENDIMENTO DIGISAC": "", "2° TENTATIVA DE CONTATO": "", "3° TENTATIVA DE CONTATO": "","CANCELAMENTO SOLICITADO": "", "ENTREGUE": "", "CANCELADO": "",
    "REENTREGA": "", "AGUARDANDO TRANSPORTADORA": "",
    "ACAREAÇÃO": "Olá, {nome_cliente}! Tudo bem?\n\nIdentificamos uma divergência na entrega do seu pedido e, por isso, abrimos um chamado de acareação com a transportadora {transportadora}.\n\nO prazo para a conclusão desta análise é de até 7 dias úteis.\n\nAtenciosamente,\n{colaborador}",
    "AUSENTE": "Olá, {nome_cliente}! Tudo bem?\n\nA transportadora {transportadora} tentou realizar a entrega, porém o responsável estava ausente.\n\nPor gentileza, confirme os dados para reentrega:\nEndereço:\nReferência:\nTelefone:\n\nAtenciosamente,\n{colaborador}",
    "EXTRAVIO": "Olá, {nome_cliente}! Tudo bem?\n\nInfelizmente a transportadora {transportadora} nos informou o extravio da sua mercadoria. Deseja o reenvio de um novo produto ou o cancelamento?\n\nAtenciosamente,\n{colaborador}"
}

modelos_sac = {
    "OUTROS": "", "RECLAME AQUI": "", "SAUDAÇÃO": "Olá, {nome_cliente}!\n\nMe chamo {colaborador} e vou prosseguir com o seu atendimento.\nComo posso ajudar?",
    "AGRADECIMENTO": "Olá, {nome_cliente}!\n\nFico feliz que tenha dado tudo certo. Estamos à disposição!\n\nAtenciosamente,\n{colaborador}",
    "SOLICITAÇÃO DE COLETA": "Olá, {nome_cliente}!\n\nO atendimento é referente ao seu pedido {numero_pedido}. Solicitamos a coleta no endereço: {endereco_resumido}.\n\nAtenciosamente,\n{colaborador}"
}

# ==========================================
#      5. CALLBACKS
# ==========================================
def registrar_e_limpar(setor, texto_pronto):
    sufixo = "_p" if setor == "Pendência" else "_s"
    st.session_state[f'texto_persistente{sufixo}'] = texto_pronto
    
    sucesso = salvar_registro(
        setor, 
        st.session_state.get(f"colab{sufixo}"),
        st.session_state.get(f"msg{sufixo}"),
        st.session_state.get(f"portal{sufixo}"),
        st.session_state.get(f"nf{sufixo}"),
        st.session_state.get(f"ped{sufixo}"),
        st.session_state.get(f"crm{sufixo}"),
        st.session_state.get(f"transp_p", "-") if setor == "Pendência" else "-"
    )
    
    if sucesso:
        st.session_state[f'sucesso_recente{sufixo}'] = True
        for campo in [f"cliente{sufixo}", f"nf{sufixo}", f"ped{sufixo}", "end_coleta_sac"]:
            if campo in st.session_state: st.session_state[campo] = ""

# ==========================================
#      6. PÁGINAS
# ==========================================
def pagina_pendencias():
    if st.session_state.get('sucesso_recente_p'):
        st.toast("Registrado com sucesso!", icon="✅")
        st.session_state['sucesso_recente_p'] = False

    st.title("🚚 Pendências Logísticas")
    c1, c2, c3 = st.columns(3)
    colab = c1.selectbox("👤 Colaborador:", colaboradores_pendencias, key="colab_p")
    cliente = c2.text_input("👤 Nome do Cliente:", key="cliente_p")
    portal = c3.selectbox("🛒 Portal:", lista_portais, key="portal_p")

    c4, c5, c6, c7 = st.columns(4)
    nf = c4.text_input("📄 Nota Fiscal:", key="nf_p")
    ped = c5.text_input("📦 Pedido:", key="ped_p")
    crm = c6.selectbox("📂 Motivo CRM:", lista_motivo_crm, key="crm_p")
    transp = c7.selectbox("🚛 Transportadora:", lista_transportadoras, key="transp_p")

    opcao = st.selectbox("Selecione o caso:", sorted(modelos_pendencias.keys()), key="msg_p")
    
    texto_base = modelos_pendencias[opcao]
    nome_f = cliente if cliente else "(Nome do cliente)"
    assina = colab if "AMAZON" not in portal else ""
    texto_final = texto_base.replace("{nome_cliente}", nome_f).replace("{transportadora}", transp).replace("{colaborador}", assina)
    
    if ped and opcao not in ["ENTREGUE", "CANCELADO"]:
        texto_final = f"O atendimento é referente ao seu pedido de número {ped}\n\n" + texto_final

    st.markdown(f'<div class="preview-box">{texto_final}</div>', unsafe_allow_html=True)
    if st.button("✅ Registrar e Copiar", key="btn_p"):
        registrar_e_limpar("Pendência", texto_final)
        copiar_para_clipboard(texto_final)
        st.rerun()

def pagina_sac():
    if st.session_state.get('sucesso_recente_s'):
        st.toast("Registrado com sucesso!", icon="✅")
        st.session_state['sucesso_recente_s'] = False

    st.title("🎧 SAC / Atendimento")
    c1, c2, c3 = st.columns(3)
    colab = c1.selectbox("👤 Colaborador:", colaboradores_sac, key="colab_s")
    cliente = c2.text_input("👤 Nome do Cliente:", key="cliente_s")
    portal = c3.selectbox("🛒 Portal:", lista_portais, key="portal_s")

    c4, c5, c6 = st.columns(3)
    nf = c4.text_input("📄 Nota Fiscal:", key="nf_s")
    ped = c5.text_input("📦 Pedido:", key="ped_s")
    crm = c6.selectbox("📂 Motivo CRM:", lista_motivo_crm, key="crm_s")

    opcao = st.selectbox("💬 Motivo do contato:", sorted(modelos_sac.keys()), key="msg_s")
    
    dados_extra = {}
    if opcao == "SOLICITAÇÃO DE COLETA":
        dados_extra["{endereco_resumido}"] = st.text_input("Endereço da coleta:", key="end_coleta_sac")

    texto_base = modelos_sac[opcao]
    nome_f = cliente if cliente else "(Nome do cliente)"
    assina = colab if "AMAZON" not in portal else ""
    texto_final = texto_base.replace("{nome_cliente}", nome_f).replace("{colaborador}", assina).replace("{numero_pedido}", ped)
    for k, v in dados_extra.items(): texto_final = texto_final.replace(k, v if v else "...")

    st.markdown(f'<div class="preview-box">{texto_final}</div>', unsafe_allow_html=True)
    if st.button("✅ Registrar e Copiar", key="btn_s"):
        registrar_e_limpar("SAC", texto_final)
        copiar_para_clipboard(texto_final)
        st.rerun()

def pagina_dashboard():
    st.title("📊 Dashboard Gerencial")
    df = carregar_dados()
    if not df.empty:
        df["Data_Filtro"] = pd.to_datetime(df["Data"], format="%d/%m/%Y", errors='coerce')
        st.metric("Total de Atendimentos", len(df), border=True)
        
        # Gráfico Simples
        fig = px.histogram(df, x="Dia_Semana", color="Setor", barmode="group", title="Atendimentos por Dia")
        st.plotly_chart(fig, use_container_width=True)
        
        st.dataframe(df.sort_values(by="Hora", ascending=False), use_container_width=True)
    else:
        st.info("Nenhum dado para exibir.")

# ==========================================
#      7. EXECUÇÃO
# ==========================================
if pagina_escolhida == "Pendências Logísticas": pagina_pendencias()
elif pagina_escolhida == "SAC / Atendimento": pagina_sac()
else: pagina_dashboard()
