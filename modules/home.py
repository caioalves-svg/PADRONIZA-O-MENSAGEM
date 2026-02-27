from datetime import date

import streamlit as st

from modules.sheets import carregar_dados_dashboard, carregar_problemas

# ── Changelog de versões ──────────────────────────────────────────────────────
# Para adicionar nova versão: insira um novo dict NO TOPO da lista.
# Mude novidade=True APENAS na versão mais recente.
VERSOES = [
    {
        "versao": "v1.2",
        "data": "27/02/2026",
        "novidade": True,
        "features": [
            {
                "icone": "📋",
                "nome": "Diário de Problemas",
                "cor": "linear-gradient(135deg,#7c3aed,#a855f7)",
                "o_que_e": (
                    "Espaço para registrar problemas, erros e inconsistências "
                    "encontradas no atendimento. Os registros alimentam reuniões "
                    "de análise e melhoria de processos."
                ),
                "como_usar": (
                    'Acesse "Diário de Problemas" no menu lateral. '
                    "Preencha obrigatoriamente: o que aconteceu, a área afetada "
                    "e se é recorrente. Causa e sugestão são opcionais — "
                    "mas ajudam muito na análise."
                ),
            },
            {
                "icone": "💰",
                "nome": "Cobrança",
                "cor": "linear-gradient(135deg,#b45309,#f59e0b)",
                "o_que_e": (
                    "Consolida clientes que receberam o produto e foram reembolsados, "
                    "mantendo o histórico organizado para acompanhamento "
                    "e cobrança posterior."
                ),
                "como_usar": (
                    'No módulo SAC, após gerar a mensagem, marque "Direcionar para cobrança" '
                    "e informe o celular do cliente. O caso aparece automaticamente "
                    'em "Cobrança" com todos os dados do atendimento.'
                ),
            },
        ],
    },
]

_BANNER_KEY = f"novidades_vistas_{VERSOES[0]['versao'].replace('.', '')}"


def _card_feature(icone: str, nome: str, cor: str, o_que_e: str, como_usar: str) -> str:
    return (
        f'<div style="background:white;border-radius:16px;padding:1.5rem 1.5rem 1.75rem;'
        f'box-shadow:0 4px 20px -4px rgba(0,0,0,0.10);height:100%">'
        f'<div style="background:{cor};border-radius:12px;padding:0.7rem 1rem;'
        f'display:inline-flex;align-items:center;gap:0.6rem;margin-bottom:1.2rem">'
        f'<span style="font-size:1.4rem">{icone}</span>'
        f'<span style="color:white;font-weight:800;font-size:1rem">{nome}</span>'
        f'</div>'
        f'<p style="margin:0 0 0.35rem;font-size:0.78rem;font-weight:700;'
        f'text-transform:uppercase;letter-spacing:0.06em;color:#94a3b8">O que é</p>'
        f'<p style="margin:0 0 1.1rem;color:#334155;font-size:0.92rem;line-height:1.6">{o_que_e}</p>'
        f'<p style="margin:0 0 0.35rem;font-size:0.78rem;font-weight:700;'
        f'text-transform:uppercase;letter-spacing:0.06em;color:#94a3b8">Como usar</p>'
        f'<p style="margin:0;color:#334155;font-size:0.92rem;line-height:1.6">{como_usar}</p>'
        f'</div>'
    )


def _secao(titulo: str):
    st.markdown(
        f'<div style="border-left:4px solid #0369a1;padding:0.1rem 0 0.1rem 0.9rem;'
        f'margin:0 0 0.9rem">'
        f'<span style="font-size:1rem;font-weight:700;color:#1e293b">{titulo}</span>'
        f'</div>',
        unsafe_allow_html=True,
    )


def _fechar_banner():
    st.session_state[_BANNER_KEY] = True


def pagina_home():
    usuario = st.session_state.get("usuario_logado", "")
    versao_atual = VERSOES[0]

    # ── Cabeçalho ─────────────────────────────────────────────────────────────
    st.markdown(f"""
    <div style="background:linear-gradient(135deg,#0f172a 0%,#1e3a5f 55%,#0369a1 100%);
                border-radius:20px;padding:1.75rem 2rem;margin-bottom:1.25rem;color:white">
        <h1 style="margin:0;color:white;font-size:1.9rem;font-weight:800;letter-spacing:-0.5px">
            👋 Olá, {usuario or "bem-vindo(a)"}!
        </h1>
        <p style="margin:0.35rem 0 0;opacity:0.75;font-size:0.9rem">
            Sistema Integrado Engage &nbsp;·&nbsp; {versao_atual["versao"]} &nbsp;·&nbsp; {versao_atual["data"]}
        </p>
    </div>""", unsafe_allow_html=True)

    # ── Banner de novidades ────────────────────────────────────────────────────
    if versao_atual.get("novidade") and not st.session_state.get(_BANNER_KEY):
        col_b, col_x = st.columns([11, 1])
        with col_b:
            st.success(
                f"🎉 **Novidades em {versao_atual['versao']}** — "
                f"Esta versão traz {len(versao_atual['features'])} novas funcionalidades. "
                "Veja abaixo o que mudou e como usar."
            )
        with col_x:
            st.button("✕", key="btn_fechar_banner", on_click=_fechar_banner, help="Fechar aviso")

    # ── Cards das features ─────────────────────────────────────────────────────
    _secao("✨ Novidades desta versão")
    features = versao_atual["features"]
    colunas = st.columns(len(features))
    for col, feat in zip(colunas, features):
        with col:
            st.markdown(
                _card_feature(
                    feat["icone"], feat["nome"], feat["cor"],
                    feat["o_que_e"], feat["como_usar"],
                ),
                unsafe_allow_html=True,
            )

    # ── Histórico de versões anteriores ───────────────────────────────────────
    versoes_anteriores = VERSOES[1:]
    if versoes_anteriores:
        st.markdown("<div style='margin-top:0.75rem'></div>", unsafe_allow_html=True)
        with st.expander("📜 Versões anteriores"):
            for v in versoes_anteriores:
                st.markdown(f"**{v['versao']}** · {v['data']}")
                for feat in v["features"]:
                    st.markdown(f"- {feat['icone']} **{feat['nome']}** — {feat['o_que_e']}")
                st.markdown("---")

    st.markdown("<div style='margin-top:2rem'></div>", unsafe_allow_html=True)

    # ── Resumo do dia ──────────────────────────────────────────────────────────
    _secao("📊 Resumo do dia")
    hoje_str = date.today().strftime("%d/%m/%Y")

    try:
        df = carregar_dados_dashboard()
        if not df.empty and "Data" in df.columns:
            df_hoje = df[df["Data"] == hoje_str]
            total_hoje = len(df_hoje)
            sac_hoje   = int((df_hoje["Setor"] == "SAC").sum())   if "Setor" in df_hoje.columns else 0
            pend_hoje  = int((df_hoje["Setor"] == "Pendência").sum()) if "Setor" in df_hoje.columns else 0

            m1, m2, m3 = st.columns(3)
            m1.metric("Atendimentos hoje", total_hoje)
            m2.metric("SAC", sac_hoje)
            m3.metric("Pendências", pend_hoje)
        else:
            st.caption("Sem dados disponíveis no momento.")
    except Exception:
        st.caption("Sem dados disponíveis no momento.")

    st.markdown("<div style='margin-top:2rem'></div>", unsafe_allow_html=True)

    # ── Últimos problemas registrados ─────────────────────────────────────────
    _secao("📋 Últimos problemas registrados")
    try:
        df_prob = carregar_problemas()
        if df_prob.empty:
            st.info("Nenhum problema registrado ainda. Seja o primeiro a contribuir!")
        else:
            cols_exibir = [
                c for c in ["Data", "Hora", "Colaborador", "Area", "Descricao", "Gravidade", "Recorrente"]
                if c in df_prob.columns
            ]
            ultimos = df_prob[cols_exibir].tail(5).iloc[::-1]
            st.dataframe(ultimos, use_container_width=True, hide_index=True)
    except Exception:
        st.caption("Não foi possível carregar os problemas registrados.")
