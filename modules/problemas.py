import time

import streamlit as st

from modules.sheets import salvar_problema, carregar_problemas

_COOLDOWN = 30

AREAS = [
    "SAC / Atendimento",
    "Logística / Pendências",
    "Cobrança",
    "Geral / Outro",
]

RECORRENCIAS = [
    "Primeira vez",
    "Já aconteceu antes",
    "Acontece com frequência",
]

GRAVIDADES = ["", "Baixa", "Média", "Alta"]


def _callback_salvar_problema(colab: str):
    ultimo_tempo = st.session_state.get("_ultimo_save_prob", 0.0)
    decorrido = time.time() - ultimo_tempo

    if decorrido < _COOLDOWN:
        restante = int(_COOLDOWN - decorrido)
        st.session_state["_aviso_dup_prob"] = restante
        return

    if st.session_state.get("_salvando_prob"):
        return
    st.session_state["_salvando_prob"] = True

    dados = {
        "colaborador": colab,
        "area":        st.session_state.get("area_prob", ""),
        "descricao":   st.session_state.get("desc_prob", ""),
        "recorrente":  st.session_state.get("recorr_prob", ""),
        "gravidade":   st.session_state.get("grav_prob", ""),
        "causa":       st.session_state.get("causa_prob", ""),
        "sugestao":    st.session_state.get("sug_prob", ""),
        "referencia":  st.session_state.get("ref_prob", ""),
    }

    sucesso = salvar_problema(dados)
    st.session_state["_salvando_prob"] = False

    if sucesso:
        st.session_state["_ultimo_save_prob"] = time.time()
        st.session_state["sucesso_prob"] = True
        for campo in ["desc_prob", "causa_prob", "sug_prob", "ref_prob"]:
            if campo in st.session_state:
                st.session_state[campo] = ""
    else:
        st.session_state["erro_prob"] = True


def _limpar_prob():
    for campo in ["desc_prob", "causa_prob", "sug_prob", "ref_prob"]:
        if campo in st.session_state:
            st.session_state[campo] = ""
    st.session_state.pop("_ultimo_save_prob", None)


def pagina_problemas():
    if st.session_state.pop("sucesso_prob", False):
        st.toast("Problema registrado com sucesso!", icon="\u2705")
    if st.session_state.pop("erro_prob", False):
        st.error("\u26a0\ufe0f Falha ao salvar. Tente novamente.")

    aviso = st.session_state.pop("_aviso_dup_prob", None)
    if aviso is not None:
        st.warning(f"\u26a0\ufe0f Aguarde {aviso}s antes de registrar novamente.")

    st.markdown("""
    <div style="background:linear-gradient(135deg,#7c3aed 0%,#a855f7 55%,#ec4899 100%);
                border-radius:20px;padding:1.75rem 2rem;margin-bottom:1.25rem;color:white">
        <h1 style="margin:0;color:white;font-size:1.9rem;font-weight:800;letter-spacing:-0.5px">
            \U0001f4cb Di\u00e1rio de Problemas
        </h1>
        <p style="margin:0.35rem 0 0;opacity:0.85;font-size:0.9rem">
            Registre problemas, inconsist\u00eancias e li\u00e7\u00f5es aprendidas para an\u00e1lise e melhoria cont\u00ednua
        </p>
    </div>""", unsafe_allow_html=True)

    colab = st.session_state.get("usuario_logado", "")

    aba_registrar, aba_consultar = st.tabs([
        "\u2795 Registrar Problema",
        "\U0001f50d Consultar Registros",
    ])

    # ── ABA 1: REGISTRAR ──────────────────────────────────────────────────────
    with aba_registrar:
        st.markdown("""<div style="border-left:4px solid #7c3aed;padding:0.1rem 0 0.1rem 0.9rem;margin:0.9rem 0">
            <span style="font-size:1rem;font-weight:700;color:#1e293b">Campos Obrigat\u00f3rios</span>
        </div>""", unsafe_allow_html=True)

        c1, c2, c3 = st.columns(3)
        with c1:
            st.selectbox("\U0001f464 Colaborador:", [colab], disabled=True)
        with c2:
            st.selectbox("\U0001f3f7\ufe0f \u00c1rea afetada: *", AREAS, key="area_prob")
        with c3:
            st.selectbox("\U0001f501 \u00c9 recorrente? *", RECORRENCIAS, key="recorr_prob")

        st.text_area(
            "\U0001f4dd O que aconteceu? *",
            key="desc_prob",
            height=140,
            placeholder=(
                "Descreva o problema com o m\u00e1ximo de detalhes que puder. "
                "O que aconteceu, quando, como, qual o impacto..."
            ),
        )

        st.markdown("""<div style="border-left:4px solid #a855f7;padding:0.1rem 0 0.1rem 0.9rem;margin:0.9rem 0">
            <span style="font-size:1rem;font-weight:700;color:#1e293b">Campos Opcionais</span>
            <span style="font-size:0.82rem;color:#64748b;margin-left:0.5rem">
                — quanto mais voc\u00ea preencher, melhor a an\u00e1lise
            </span>
        </div>""", unsafe_allow_html=True)

        c4, c5 = st.columns(2)
        with c4:
            st.selectbox(
                "\u26a1 Gravidade:",
                GRAVIDADES,
                key="grav_prob",
                format_func=lambda x: x if x else "— N\u00e3o informado —",
            )
        with c5:
            st.text_input(
                "\U0001f517 NF / N\u00ba Pedido relacionado:",
                key="ref_prob",
                placeholder="Opcional — preencha se o problema envolve um pedido espec\u00edfico",
            )

        st.text_area(
            "\U0001f50d Qual a poss\u00edvel causa?",
            key="causa_prob",
            height=100,
            placeholder="Se souber ou suspeitar, descreva a causa raiz...",
        )

        st.text_area(
            "\U0001f4a1 Sugest\u00e3o de melhoria:",
            key="sug_prob",
            height=100,
            placeholder="Tem alguma ideia de como evitar que isso aconte\u00e7a novamente?",
        )

        descricao = st.session_state.get("desc_prob", "")
        faltando = not descricao.strip()

        st.markdown("<hr style='margin:0.75rem 0;border-color:#e2e8f0'>", unsafe_allow_html=True)

        col_btn1, col_btn2 = st.columns([3, 1])
        with col_btn1:
            st.button(
                "\u2705 Registrar Problema",
                key="btn_save_prob",
                on_click=_callback_salvar_problema,
                args=(colab,),
                disabled=faltando,
                type="primary",
                use_container_width=True,
            )
        with col_btn2:
            st.button(
                "\U0001f5d1\ufe0f Limpar",
                key="btn_limpar_prob",
                on_click=_limpar_prob,
                use_container_width=True,
            )

        if faltando:
            st.caption("\u26a0\ufe0f O campo **O que aconteceu?** \u00e9 obrigat\u00f3rio.")

    # ── ABA 2: CONSULTAR ─────────────────────────────────────────────────────
    with aba_consultar:
        st.markdown("""<div style="border-left:4px solid #7c3aed;padding:0.1rem 0 0.1rem 0.9rem;margin:0.9rem 0">
            <span style="font-size:1rem;font-weight:700;color:#1e293b">Registros de Problemas</span>
        </div>""", unsafe_allow_html=True)

        col_refresh, _ = st.columns([1, 5])
        with col_refresh:
            if st.button("\U0001f504 Atualizar", key="btn_refresh_prob"):
                carregar_problemas.clear()

        df = carregar_problemas()

        if df.empty:
            st.info("\U0001f4ed Nenhum problema registrado ainda.")
        else:
            c_f1, c_f2, c_f3 = st.columns(3)
            with c_f1:
                areas_disp = ["Todos"] + sorted(df["Area"].dropna().unique().tolist())
                filtro_area = st.selectbox("Filtrar por \u00e1rea:", areas_disp, key="f_area_prob")
            with c_f2:
                grav_disp = ["Todos"] + [g for g in ["Alta", "M\u00e9dia", "Baixa"] if g in df["Gravidade"].values]
                filtro_grav = st.selectbox("Filtrar por gravidade:", grav_disp, key="f_grav_prob")
            with c_f3:
                filtro_recorr = st.selectbox(
                    "Recorr\u00eancia:",
                    ["Todos"] + RECORRENCIAS,
                    key="f_rec_prob",
                )

            dff = df.copy()
            if filtro_area != "Todos":
                dff = dff[dff["Area"] == filtro_area]
            if filtro_grav != "Todos":
                dff = dff[dff["Gravidade"] == filtro_grav]
            if filtro_recorr != "Todos":
                dff = dff[dff["Recorrente"] == filtro_recorr]

            st.caption(f"{len(dff)} registro(s) encontrado(s) de {len(df)} no total")
            st.dataframe(dff, use_container_width=True, hide_index=True)

            if not dff.empty:
                csv = dff.to_csv(index=False).encode("utf-8-sig")
                st.download_button(
                    "\u2b07\ufe0f Exportar CSV",
                    data=csv,
                    file_name="problemas_registrados.csv",
                    mime="text/csv",
                )
