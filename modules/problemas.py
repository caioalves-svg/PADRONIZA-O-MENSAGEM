import json
import os
import time
from datetime import date, datetime

import streamlit as st

from modules.sheets import salvar_problema, carregar_problemas, atualizar_problema

_COOLDOWN = 30

GESTORA = "Larissa Plácido"

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

STATUS_OPCOES = ["Pendente", "Em Análise", "Em Observação", "Resolvido", "Descartado"]

PRIORIDADES = ["", "Baixa", "Média", "Alta", "Crítica"]

TIPO_SOLUCAO = ["", "Paliativa", "Definitiva", "Paliativa + Definitiva em andamento"]

TAGS = {
    "Processo": "Fluxo ou etapa do processo operacional com falha",
    "Treinamento": "Problema de conhecimento ou falta de capacitação da equipe",
    "Sistema": "Bug, lentidão ou comportamento inesperado em ferramenta/sistema",
    "Transportadora": "Falha, atraso ou divergência com transportadora",
    "Portal": "Problema no portal de vendas (B2B, B2C, marketplace)",
    "Comunicação Interna": "Informação não transmitida corretamente entre equipes",
    "Regra de Negócio": "Regra inexistente, ambígua ou não seguida",
}


def _carregar_responsaveis() -> list:
    json_path = os.path.join(os.path.dirname(__file__), "..", "data", "lists.json")
    try:
        with open(json_path, encoding="utf-8") as f:
            data = json.load(f)
        todos = set(data.get("colaboradores_sac", []) + data.get("colaboradores_pendencias", []))
        return [""] + sorted(todos)
    except Exception:
        return [""]


def _dias_aberto(data_str: str) -> int:
    try:
        d = datetime.strptime(data_str, "%d/%m/%Y").date()
        return (date.today() - d).days
    except Exception:
        return 0


# ── Callbacks ─────────────────────────────────────────────────────────────────

def _callback_salvar_problema(colab: str):
    ultimo_tempo = st.session_state.get("_ultimo_save_prob", 0.0)
    decorrido = time.time() - ultimo_tempo

    if decorrido < _COOLDOWN:
        st.session_state["_aviso_dup_prob"] = int(_COOLDOWN - decorrido)
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


# ── Tab 1: Registrar ──────────────────────────────────────────────────────────

def _tab_registrar(colab: str):
    st.markdown("""<div style="border-left:4px solid #7c3aed;padding:0.1rem 0 0.1rem 0.9rem;margin:0.9rem 0">
        <span style="font-size:1rem;font-weight:700;color:#1e293b">Campos Obrigatórios</span>
    </div>""", unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.selectbox("👤 Colaborador:", [colab], disabled=True)
    with c2:
        st.selectbox("🏷️ Área afetada: *", AREAS, key="area_prob")
    with c3:
        st.selectbox("🔁 É recorrente? *", RECORRENCIAS, key="recorr_prob")

    st.text_area(
        "📝 O que aconteceu? *",
        key="desc_prob",
        height=140,
        placeholder=(
            "Descreva o problema com o máximo de detalhes que puder. "
            "O que aconteceu, quando, como, qual o impacto..."
        ),
    )

    st.markdown("""<div style="border-left:4px solid #a855f7;padding:0.1rem 0 0.1rem 0.9rem;margin:0.9rem 0">
        <span style="font-size:1rem;font-weight:700;color:#1e293b">Campos Opcionais</span>
        <span style="font-size:0.82rem;color:#64748b;margin-left:0.5rem">
            — quanto mais você preencher, melhor a análise
        </span>
    </div>""", unsafe_allow_html=True)

    c4, c5 = st.columns(2)
    with c4:
        st.selectbox(
            "⚡ Gravidade:",
            GRAVIDADES,
            key="grav_prob",
            format_func=lambda x: x if x else "— Não informado —",
        )
    with c5:
        st.text_input(
            "🔗 NF / Nº Pedido relacionado:",
            key="ref_prob",
            placeholder="Opcional — preencha se o problema envolve um pedido específico",
        )

    st.text_area(
        "🔍 Qual a possível causa?",
        key="causa_prob",
        height=100,
        placeholder="Se souber ou suspeitar, descreva a causa raiz...",
    )

    st.text_area(
        "💡 Sugestão de melhoria:",
        key="sug_prob",
        height=100,
        placeholder="Tem alguma ideia de como evitar que isso aconteça novamente?",
    )

    descricao = st.session_state.get("desc_prob", "")
    faltando = not descricao.strip()

    st.markdown("<hr style='margin:0.75rem 0;border-color:#e2e8f0'>", unsafe_allow_html=True)

    col_btn1, col_btn2 = st.columns([3, 1])
    with col_btn1:
        st.button(
            "✅ Registrar Problema",
            key="btn_save_prob",
            on_click=_callback_salvar_problema,
            args=(colab,),
            disabled=faltando,
            type="primary",
            use_container_width=True,
        )
    with col_btn2:
        st.button(
            "🗑️ Limpar",
            key="btn_limpar_prob",
            on_click=_limpar_prob,
            use_container_width=True,
        )

    if faltando:
        st.caption("⚠️ O campo **O que aconteceu?** é obrigatório.")


# ── Tab 2: Quadro Público ─────────────────────────────────────────────────────

def _tab_quadro_publico():
    st.markdown("""<div style="border-left:4px solid #0369a1;padding:0.1rem 0 0.1rem 0.9rem;margin:0.9rem 0">
        <span style="font-size:1rem;font-weight:700;color:#1e293b">Tarefas em andamento</span>
        <span style="font-size:0.82rem;color:#64748b;margin-left:0.5rem">
            — problemas sob análise ou em observação
        </span>
    </div>""", unsafe_allow_html=True)

    col_r, _ = st.columns([1, 5])
    with col_r:
        if st.button("🔄 Atualizar", key="btn_refresh_quadro"):
            carregar_problemas.clear()

    df = carregar_problemas()

    if df.empty or "Status" not in df.columns:
        st.info("📭 Nenhum problema registrado ainda.")
        return

    status_ativos = ["Em Análise", "Em Observação"]
    df_ativos = df[df["Status"].isin(status_ativos)].copy()

    if df_ativos.empty:
        st.success("✅ Nenhuma tarefa em aberto no momento! Tudo resolvido.")
        return

    # Calcula dias em aberto
    if "Data" in df_ativos.columns:
        df_ativos["Dias em aberto"] = df_ativos["Data"].apply(_dias_aberto)

    # Coluna de exibição: usa Titulo se preenchido, senão trunca Descricao
    df_ativos["Assunto"] = df_ativos.apply(
        lambda r: str(r.get("Titulo", "")).strip() or (str(r.get("Descricao", ""))[:70] + "…"),
        axis=1,
    )

    # Ordena por responsável e dias em aberto (mais antigos primeiro)
    sort_cols = [c for c in ["Responsavel", "Dias em aberto"] if c in df_ativos.columns]
    if sort_cols:
        df_ativos = df_ativos.sort_values(sort_cols, ascending=[True, False])

    cols_show = [c for c in ["Assunto", "Area", "Responsavel", "Status", "Prioridade", "Dias em aberto"]
                 if c in df_ativos.columns]

    st.caption(f"{len(df_ativos)} tarefa(s) em andamento")
    st.dataframe(df_ativos[cols_show], use_container_width=True, hide_index=True)

    # Legenda de tags
    with st.expander("📖 Legenda de tags"):
        for tag, desc in TAGS.items():
            st.markdown(f"- **{tag}** — {desc}")


# ── Tab 3: Gestão (Larissa Plácido only) ─────────────────────────────────────

def _form_gestao(row, responsaveis: list, prefix: str):
    """Renderiza formulário de gestão para um problema. Retorna True se salvo com sucesso."""
    problema_id = str(row.get("ID", "")).strip()

    # Detalhes do problema (leitura)
    st.caption(
        f"**Colaborador:** {row.get('Colaborador', '—')} &nbsp;|&nbsp; "
        f"**Área:** {row.get('Area', '—')} &nbsp;|&nbsp; "
        f"**Data:** {row.get('Data', '—')} {row.get('Hora', '')}"
    )
    st.markdown(f"**O que aconteceu:** {row.get('Descricao', '')}")
    if str(row.get("Causa", "")).strip():
        st.markdown(f"**Possível causa:** {row.get('Causa')}")
    if str(row.get("Sugestao", "")).strip():
        st.markdown(f"**Sugestão:** {row.get('Sugestao')}")
    if str(row.get("Referencia", "")).strip():
        st.caption(f"Referência: {row.get('Referencia')}")

    st.markdown("---")

    with st.form(key=f"form_{prefix}_{problema_id}"):
        c1, c2 = st.columns(2)
        with c1:
            novo_titulo = st.text_input(
                "Título resumido",
                value=str(row.get("Titulo", "")),
                placeholder="Ex.: Falha de etiqueta na Jadlog",
            )
        with c2:
            idx_status = STATUS_OPCOES.index(row.get("Status", "Pendente")) if row.get("Status") in STATUS_OPCOES else 0
            novo_status = st.selectbox("Status", STATUS_OPCOES, index=idx_status)

        c3, c4 = st.columns(2)
        with c3:
            prio_val = str(row.get("Prioridade", ""))
            idx_prio = PRIORIDADES.index(prio_val) if prio_val in PRIORIDADES else 0
            nova_prioridade = st.selectbox(
                "Prioridade",
                PRIORIDADES,
                index=idx_prio,
                format_func=lambda x: x if x else "— Não definida —",
            )
        with c4:
            resp_val = str(row.get("Responsavel", ""))
            idx_resp = responsaveis.index(resp_val) if resp_val in responsaveis else 0
            novo_resp = st.selectbox(
                "Responsável pela análise",
                responsaveis,
                index=idx_resp,
                format_func=lambda x: x if x else "— Não atribuído —",
            )

        tags_atuais = [t.strip() for t in str(row.get("Tags", "")).split(";") if t.strip() and t.strip() in TAGS]
        novas_tags = st.multiselect(
            "Tags",
            options=list(TAGS.keys()),
            default=tags_atuais,
            help=" | ".join(f"**{k}**: {v}" for k, v in TAGS.items()),
        )

        tipo_val = str(row.get("TipoSolucao", ""))
        idx_tipo = TIPO_SOLUCAO.index(tipo_val) if tipo_val in TIPO_SOLUCAO else 0
        novo_tipo = st.selectbox(
            "Tipo de solução",
            TIPO_SOLUCAO,
            index=idx_tipo,
            format_func=lambda x: x if x else "— Não definido —",
        )

        nova_acao = st.text_area(
            "Ação tomada",
            value=str(row.get("AcaoTomada", "")),
            height=80,
            placeholder="Descreva o que foi feito ou decidido...",
        )

        doc_gerado = st.checkbox(
            "Documento / POP gerado",
            value=str(row.get("DocumentoGerado", "")).upper() == "TRUE",
        )

        salvo = st.form_submit_button("💾 Salvar", type="primary", use_container_width=True)

    if salvo:
        campos = {
            "Titulo":         novo_titulo,
            "Status":         novo_status,
            "Prioridade":     nova_prioridade,
            "Responsavel":    novo_resp,
            "Tags":           "; ".join(novas_tags),
            "TipoSolucao":    novo_tipo,
            "AcaoTomada":     nova_acao,
            "DocumentoGerado": "TRUE" if doc_gerado else "FALSE",
        }
        ok = atualizar_problema(problema_id, campos)
        if ok:
            st.toast("Salvo com sucesso!", icon="✅")
            st.rerun()
        else:
            st.error("⚠️ Falha ao salvar. Verifique a conexão e tente novamente.")


def _tab_gestao():
    col_r, _ = st.columns([1, 5])
    with col_r:
        if st.button("🔄 Atualizar", key="btn_refresh_gestao"):
            carregar_problemas.clear()

    df = carregar_problemas()
    responsaveis = _carregar_responsaveis()

    if df.empty or "Status" not in df.columns:
        st.info("📭 Nenhum problema registrado ainda.")
        return

    # ── Seção 1: Fila de Triagem ──────────────────────────────────────────────
    df_pend = df[df["Status"] == "Pendente"].copy()

    st.markdown(
        f"""<div style="border-left:4px solid #f59e0b;padding:0.1rem 0 0.1rem 0.9rem;margin:1.2rem 0 0.6rem">
        <span style="font-size:1rem;font-weight:700;color:#1e293b">
            📬 Fila de Triagem — {len(df_pend)} pendente(s)
        </span></div>""",
        unsafe_allow_html=True,
    )

    if df_pend.empty:
        st.success("✅ Nenhum problema pendente de triagem!")
    else:
        for _, row in df_pend.iterrows():
            pid = str(row.get("ID", "")).strip()
            if not pid:
                continue
            desc_prev = str(row.get("Descricao", ""))[:70]
            label = f"📬 {desc_prev}{'…' if len(str(row.get('Descricao',''))) > 70 else ''} — {row.get('Area', '')}"
            with st.expander(label):
                _form_gestao(row, responsaveis, "pend")

    st.markdown("<div style='margin-top:0.5rem'></div>", unsafe_allow_html=True)

    # ── Seção 2: Em Andamento ─────────────────────────────────────────────────
    df_and = df[df["Status"].isin(["Em Análise", "Em Observação"])].copy()

    if "Data" in df_and.columns:
        df_and["_dias"] = df_and["Data"].apply(_dias_aberto)

    st.markdown(
        f"""<div style="border-left:4px solid #0369a1;padding:0.1rem 0 0.1rem 0.9rem;margin:1.2rem 0 0.6rem">
        <span style="font-size:1rem;font-weight:700;color:#1e293b">
            🔄 Em Andamento — {len(df_and)} tarefa(s)
        </span></div>""",
        unsafe_allow_html=True,
    )

    if df_and.empty:
        st.info("Nenhuma tarefa em andamento.")
    else:
        if "_dias" in df_and.columns:
            df_and = df_and.sort_values("_dias", ascending=False)
        for _, row in df_and.iterrows():
            pid = str(row.get("ID", "")).strip()
            if not pid:
                continue
            titulo = str(row.get("Titulo", "")).strip() or str(row.get("Descricao", ""))[:60]
            resp = str(row.get("Responsavel", "")).strip() or "—"
            dias = int(row.get("_dias", 0)) if "_dias" in row else 0
            status_lbl = row.get("Status", "")
            label = f"🔄 {titulo} — {resp} — {dias}d — {status_lbl}"
            with st.expander(label):
                _form_gestao(row, responsaveis, "and")

    st.markdown("<div style='margin-top:0.5rem'></div>", unsafe_allow_html=True)

    # ── Seção 3: Histórico ────────────────────────────────────────────────────
    df_hist = df[df["Status"].isin(["Resolvido", "Descartado"])].copy()

    st.markdown(
        f"""<div style="border-left:4px solid #10b981;padding:0.1rem 0 0.1rem 0.9rem;margin:1.2rem 0 0.6rem">
        <span style="font-size:1rem;font-weight:700;color:#1e293b">
            📁 Histórico — {len(df_hist)} registro(s)
        </span></div>""",
        unsafe_allow_html=True,
    )

    if df_hist.empty:
        st.info("Nenhum problema resolvido ou descartado ainda.")
    else:
        cols_hist = [c for c in ["Data", "Area", "Titulo", "Status", "Responsavel", "TipoSolucao", "DocumentoGerado"]
                     if c in df_hist.columns]
        # Titulo fallback
        if "Titulo" in df_hist.columns:
            df_hist["Titulo"] = df_hist.apply(
                lambda r: str(r.get("Titulo", "")).strip() or str(r.get("Descricao", ""))[:60],
                axis=1,
            )
        st.dataframe(df_hist[cols_hist].iloc[::-1], use_container_width=True, hide_index=True)

        if not df_hist.empty:
            csv = df_hist.to_csv(index=False).encode("utf-8-sig")
            st.download_button(
                "⬇️ Exportar histórico CSV",
                data=csv,
                file_name="historico_problemas.csv",
                mime="text/csv",
            )


# ── Página principal ──────────────────────────────────────────────────────────

def pagina_problemas():
    if st.session_state.pop("sucesso_prob", False):
        st.toast("Problema registrado com sucesso!", icon="✅")
    if st.session_state.pop("erro_prob", False):
        st.error("⚠️ Falha ao salvar. Tente novamente.")

    aviso = st.session_state.pop("_aviso_dup_prob", None)
    if aviso is not None:
        st.warning(f"⚠️ Aguarde {aviso}s antes de registrar novamente.")

    st.markdown("""\
    <div style="background:linear-gradient(135deg,#7c3aed 0%,#a855f7 55%,#ec4899 100%);
                border-radius:20px;padding:1.75rem 2rem;margin-bottom:1.25rem;color:white">
        <h1 style="margin:0;color:white;font-size:1.9rem;font-weight:800;letter-spacing:-0.5px">
            📋 Diário de Problemas
        </h1>
        <p style="margin:0.35rem 0 0;opacity:0.85;font-size:0.9rem">
            Registre problemas, inconsistências e lições aprendidas para análise e melhoria contínua
        </p>
    </div>""", unsafe_allow_html=True)

    usuario = st.session_state.get("usuario_logado", "")
    colab = usuario

    tab_names = ["➕ Registrar Problema", "📊 Quadro Público"]
    if usuario == GESTORA:
        tab_names.append("🛠️ Gestão")

    tabs = st.tabs(tab_names)

    with tabs[0]:
        _tab_registrar(colab)

    with tabs[1]:
        _tab_quadro_publico()

    if len(tabs) > 2:
        with tabs[2]:
            _tab_gestao()
