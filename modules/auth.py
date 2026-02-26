import os

import streamlit as st

from modules.templates import carregar_listas


def tela_login() -> bool:
    """Renderiza a tela de login centralizada com logo. Retorna True se bem-sucedido."""
    listas = carregar_listas()
    colaboradores = sorted(
        set(listas["colaboradores_pendencias"] + listas["colaboradores_sac"])
    )

    st.markdown(
        '<style>'
        'section[data-testid="stMain"] > div:first-child {'
        '  background: linear-gradient(160deg, #eff6ff 0%, #f1f5f9 60%, #ede9fe 100%);'
        '  min-height: 100vh;'
        '}'
        '.block-container { padding-top: 1.5rem !important; }'
        '</style>',
        unsafe_allow_html=True,
    )

    _, col, _ = st.columns([1, 1.4, 1])

    with col:
        st.markdown("<div style='margin-top: 1rem'></div>", unsafe_allow_html=True)

        logo_path = "logo.png"
        if os.path.exists(logo_path):
            _, logo_col, _ = st.columns([1, 2, 1])
            with logo_col:
                st.image(logo_path, use_container_width=True)

        st.markdown("<div style='margin-top: 1.5rem'></div>", unsafe_allow_html=True)

        st.markdown(
            '<div style="background:white;border-radius:20px;padding:2rem 2rem 1.5rem;'
            'box-shadow:0 20px 60px -10px rgba(37,99,235,0.15),0 4px 16px rgba(0,0,0,0.06);">'
            '<h2 style="margin:0 0 0.25rem;color:#1e293b;font-size:1.4rem;font-weight:800;text-align:center">'
            'Bem-vindo(a) \U0001f44b</h2>'
            '<p style="margin:0 0 1.5rem;color:#64748b;font-size:0.9rem;text-align:center">'
            'Identifique-se para acessar o sistema</p>'
            '</div>',
            unsafe_allow_html=True,
        )

        with st.form("form_login"):
            nome_sel = st.selectbox("\U0001f464 Seu nome", colaboradores, label_visibility="visible")
            senha    = st.text_input("\U0001f511 Senha da equipe", type="password", placeholder="\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022")
            with st.expander("\u2699\ufe0f Acesso administrativo"):
                nome_adm = st.text_input(
                    "Usu\u00e1rio administrativo",
                    placeholder="Deixe em branco para uso normal",
                    label_visibility="collapsed",
                )
            st.markdown("<div style='margin-top:0.5rem'></div>", unsafe_allow_html=True)
            entrar = st.form_submit_button("Entrar \u2192", use_container_width=True, type="primary")

        nome = nome_adm.strip() if nome_adm.strip() else nome_sel

        st.markdown(
            '<p style="text-align:center;color:#94a3b8;font-size:0.78rem;margin-top:1.25rem">'
            'Sistema interno \u00b7 Engage Eletro</p>',
            unsafe_allow_html=True,
        )

    if entrar:
        try:
            senha_correta = st.secrets["auth"][nome]
        except KeyError:
            st.error("\u26a0\ufe0f Usu\u00e1rio sem senha configurada. Fale com o administrador.")
            return False
        except Exception:
            st.error("\u26a0\ufe0f Configura\u00e7\u00e3o de autentica\u00e7\u00e3o ausente. Fale com o administrador.")
            return False

        if senha == senha_correta:
            st.session_state["autenticado"]    = True
            st.session_state["usuario_logado"] = nome
            st.rerun()
        else:
            st.error("\u274c Senha incorreta. Tente novamente.")
    return False


def verificar_autenticacao() -> bool:
    """Verifica se o usu\u00e1rio est\u00e1 autenticado. Mostra login se n\u00e3o estiver."""
    if st.session_state.get("autenticado"):
        return True
    tela_login()
    return False
