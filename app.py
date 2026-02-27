import os
import streamlit as st

st.set_page_config(
    page_title="Sistema Integrado Engage",
    page_icon="\U0001f680",
    layout="wide",
)

if os.path.exists("style.css"):
    with open("style.css", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

from modules.auth import verificar_autenticacao
from modules.home import pagina_home
from modules.pendencias import pagina_pendencias
from modules.sac import pagina_sac
from modules.cobranca import pagina_cobranca
from modules.dashboard import pagina_dashboard
from modules.problemas import pagina_problemas

if not verificar_autenticacao():
    st.stop()

_usuario = st.session_state.get("usuario_logado", "")

if os.path.exists("logo.png"):
    st.sidebar.image("logo.png", use_container_width=True)

st.sidebar.markdown(
    f"<p style='margin:0.5rem 0 0.1rem;font-weight:700;color:#1e293b'>"
    f"\U0001f464 {_usuario}</p>",
    unsafe_allow_html=True,
)
st.sidebar.caption("MENU PRINCIPAL")

pagina = st.sidebar.radio(
    "Navega\u00e7\u00e3o:",
    (
        "\U0001f3e0 In\u00edcio",
        "Pend\u00eancias Log\u00edsticas",
        "SAC / Atendimento",
        "\U0001f4b0 Cobran\u00e7a",
        "\U0001f4ca Dashboard Gerencial",
        "\U0001f4cb Di\u00e1rio de Problemas",
    ),
    label_visibility="collapsed",
)

st.sidebar.markdown("---")
if st.sidebar.button("\U0001f6aa Sair", use_container_width=True):
    st.session_state.clear()
    st.rerun()

if pagina == "\U0001f3e0 In\u00edcio":
    pagina_home()
elif pagina == "Pend\u00eancias Log\u00edsticas":
    pagina_pendencias()
elif pagina == "SAC / Atendimento":
    pagina_sac()
elif pagina == "\U0001f4b0 Cobran\u00e7a":
    pagina_cobranca()
elif pagina == "\U0001f4cb Di\u00e1rio de Problemas":
    pagina_problemas()
else:
    pagina_dashboard()
