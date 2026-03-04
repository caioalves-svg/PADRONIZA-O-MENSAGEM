import json
import os
import time
from datetime import date, datetime

import streamlit as st

from modules.sheets import (
    salvar_problema, carregar_problemas, atualizar_problema,
    salvar_acompanhamento, carregar_acompanhamentos,
)

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

# ── Cores por status e prioridade ─────────────────────────────────────────────
_COR_STATUS = {
    "Em Análise":    ("#2563eb", "#eff6ff"),
    "Em Observação": ("#d97706", "#fffbeb"),
    "Pendente":      ("#7c3aed", "#faf5ff"),
    "Resolvido":     ("#16a34a", "#f0fdf4"),
    "Descartado":    ("#64748b", "#f8fafc"),
}

_COR_PRIO = {
    "Crítica": "#dc2626",
    "Alta":    "#ea580c",
    "Média":   "#ca8a04",
    "Baixa":   "#16a34a",
}

_COR_GRAV = {
    "Alta":  ("#dc2626", "#fef2f2"),
    "Média": ("#d97706", "#fffbeb"),
    "Baixa": ("#16a34a", "#f0fdf4"),
}


# ── Helpers ───────────────────────────────────────────────────────────────────

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
        return (date.today() - datetime.strptime(data_str, "%d/%m/%Y").date()).days
    except Exception:
        return 0


# ── Card: Quadro Público ──────────────────────────────────────────────────────

def _card_quadro(row, dias: int) -> str:
    status    = str(row.get("Status", ""))
    prio      = str(row.get("Prioridade", ""))
    titulo    = str(row.get("Titulo", "")).strip() or str(row.get("Descricao", ""))[:70]
    area      = str(row.get("Area", ""))
    resp_ana  = str(row.get("Responsavel", "")).strip()
    resp_trat = str(row.get("ResponsavelTratativa", "")).strip()
    tags      = [t.strip() for t in str(row.get("Tags", "")).split(";") if t.strip()]

    # Linha de responsáveis
    if resp_trat:
        resp = f"Análise: {resp_ana or '—'} &nbsp;·&nbsp; Tratativa: {resp_trat}"
    elif resp_ana:
        resp = f"Análise: {resp_ana}"
    else:
        resp = "Não atribuído"

    cor_s, bg_s = _COR_STATUS.get(status, ("#64748b", "#f8fafc"))
    cor_p       = _COR_PRIO.get(prio, "")
    cor_d       = "#16a34a" if dias < 7 else "#d97706" if dias < 15 else "#dc2626"

    prio_badge = (
        f'<span style="background:{cor_p};color:white;padding:0.12rem 0.55rem;'
        f'border-radius:99px;font-size:0.68rem;font-weight:700;margin-left:0.3rem">{prio}</span>'
    ) if prio and cor_p else ""

    tags_html = "".join(
        f'<span style="background:#f1f5f9;color:#475569;padding:0.1rem 0.45rem;'
        f'border-radius:99px;font-size:0.68rem;margin-right:0.25rem">{t}</span>'
        for t in tags
    )

    return (
        f'<div style="background:white;border-radius:14px;padding:1.2rem 1.3rem;'
        f'box-shadow:0 2px 12px -2px rgba(0,0,0,0.09);border-left:4px solid {cor_s};'
        f'margin-bottom:0.75rem">'
        f'<div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:0.6rem">'
        f'<div>'
        f'<span style="background:{bg_s};color:{cor_s};padding:0.12rem 0.6rem;'
        f'border-radius:99px;font-size:0.68rem;font-weight:700;border:1px solid {cor_s}33">{status}</span>'
        f'{prio_badge}'
        f'</div>'
        f'<span style="color:{cor_d};font-size:0.73rem;font-weight:700;white-space:nowrap">{dias}d em aberto</span>'
        f'</div>'
        f'<p style="margin:0 0 0.6rem;color:#1e293b;font-weight:700;font-size:0.88rem;line-height:1.4">{titulo}</p>'
        f'<p style="margin:0 0 0.45rem;color:#64748b;font-size:0.76rem">'
        f'<span style="background:#f8fafc;border:1px solid #e2e8f0;padding:0.1rem 0.45rem;border-radius:5px">{area}</span>'
        f'&nbsp;·&nbsp;👤 {resp}'
        f'</p>'
        f'{f"<div style=margin-top:0.4rem>{tags_html}</div>" if tags else ""}'
        f'</div>'
    )


# ── Card: Meus Registros ──────────────────────────────────────────────────────

def _card_meu_problema(row) -> str:
    desc    = str(row.get("Descricao", ""))
    impacto = str(row.get("Impacto", "")).strip()
    area    = str(row.get("Area", ""))
    grav    = str(row.get("Gravidade", ""))
    data    = str(row.get("Data", ""))
    hora    = str(row.get("Hora", ""))

    desc_prev = desc[:110] + ("…" if len(desc) > 110 else "")
    imp_prev  = impacto[:80] + ("…" if len(impacto) > 80 else "") if impacto else ""

    cor_g, bg_g = _COR_GRAV.get(grav, ("", ""))
    grav_badge = (
        f'<span style="background:{bg_g};color:{cor_g};padding:0.1rem 0.45rem;'
        f'border-radius:5px;font-size:0.73rem;font-weight:600">{grav}</span>'
    ) if grav and cor_g else ""

    impacto_html = (
        f'<p style="margin:0.4rem 0 0.5rem;color:#475569;font-size:0.8rem;line-height:1.4">'
        f'<strong>Impacto:</strong> {imp_prev}</p>'
    ) if imp_prev else ""

    return (
        f'<div style="background:white;border-radius:12px;padding:1.1rem 1.3rem;'
        f'box-shadow:0 2px 10px -2px rgba(0,0,0,0.08);border-top:3px solid #7c3aed;'
        f'margin-bottom:0.25rem">'
        f'<div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:0.5rem">'
        f'<span style="background:#faf5ff;color:#7c3aed;padding:0.1rem 0.55rem;'
        f'border-radius:99px;font-size:0.68rem;font-weight:700;border:1px solid #e9d5ff">Pendente</span>'
        f'<span style="color:#94a3b8;font-size:0.7rem">{data} {hora}</span>'
        f'</div>'
        f'<p style="margin:0 0 0;color:#334155;font-size:0.87rem;line-height:1.5">{desc_prev}</p>'
        f'{impacto_html}'
        f'<div style="display:flex;align-items:center;gap:0.4rem;flex-wrap:wrap;margin-top:0.5rem">'
        f'<span style="background:#f8fafc;border:1px solid #e2e8f0;padding:0.1rem 0.45rem;'
        f'border-radius:5px;font-size:0.73rem;color:#475569">{area}</span>'
        f'{grav_badge}'
        f'</div>'
        f'</div>'
    )


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
        "impacto":     st.session_state.get("imp_prob", ""),
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
        for campo in ["desc_prob", "imp_prob", "causa_prob", "sug_prob", "ref_prob"]:
            if campo in st.session_state:
                st.session_state[campo] = ""
    else:
        st.session_state["erro_prob"] = True


def _limpar_prob():
    for campo in ["desc_prob", "imp_prob", "causa_prob", "sug_prob", "ref_prob"]:
        if campo in st.session_state:
            st.session_state[campo] = ""
    st.session_state.pop("_ultimo_save_prob", None)


# ── Callbacks: Acompanhamento ─────────────────────────────────────────────────

_COOLDOWN_ACOMP = 30


def _callback_salvar_acompanhamento(colab: str, problem_id: str, problem_titulo: str):
    ultimo_tempo = st.session_state.get("_ultimo_save_acomp", 0.0)
    decorrido = time.time() - ultimo_tempo

    if decorrido < _COOLDOWN_ACOMP:
        st.session_state["_aviso_dup_acomp"] = int(_COOLDOWN_ACOMP - decorrido)
        return

    if st.session_state.get("_salvando_acomp"):
        return
    st.session_state["_salvando_acomp"] = True

    dados = {
        "problem_id":     problem_id,
        "problem_titulo": problem_titulo,
        "colaborador":    colab,
        "atualizacao":    st.session_state.get("atualizacao_acomp", ""),
    }

    sucesso = salvar_acompanhamento(dados)
    st.session_state["_salvando_acomp"] = False

    if sucesso:
        st.session_state["_ultimo_save_acomp"] = time.time()
        st.session_state["sucesso_acomp"] = True
        if "atualizacao_acomp" in st.session_state:
            st.session_state["atualizacao_acomp"] = ""
    else:
        st.session_state["erro_acomp"] = True


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

    col_desc, col_imp = st.columns(2)
    with col_desc:
        st.text_area(
            "📝 O que aconteceu? *",
            key="desc_prob",
            height=140,
            placeholder="Descreva o problema com o máximo de detalhes — o que aconteceu, quando, como...",
        )
    with col_imp:
        st.text_area(
            "⚡ Qual o impacto?",
            key="imp_prob",
            height=140,
            placeholder="Ex.: cliente ficou sem resposta, pedido atrasou, dado incorreto no sistema...",
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
            "🔥 Gravidade:",
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
        height=90,
        placeholder="Se souber ou suspeitar, descreva a causa raiz...",
    )

    st.text_area(
        "💡 Sugestão de melhoria:",
        key="sug_prob",
        height=90,
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


# ── Tab 2: Quadro Público (cards) ─────────────────────────────────────────────

def _tab_quadro_publico():
    st.markdown("""<div style="border-left:4px solid #0369a1;padding:0.1rem 0 0.1rem 0.9rem;margin:0.9rem 0">
        <span style="font-size:1rem;font-weight:700;color:#1e293b">Quadro de Problemas</span>
        <span style="font-size:0.82rem;color:#64748b;margin-left:0.5rem">
            — todos os problemas em aberto da equipe
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

    df_ativos = df[~df["Status"].isin(["Resolvido", "Descartado"])].copy()

    if df_ativos.empty:
        st.success("✅ Nenhum problema em aberto no momento!")
        return

    if "Data" in df_ativos.columns:
        df_ativos["_dias"] = df_ativos["Data"].apply(_dias_aberto)
    else:
        df_ativos["_dias"] = 0

    # Ordena: Em Análise → Em Observação → Pendente; dentro de cada status, mais antigos primeiro
    _STATUS_ORDER = {"Em Análise": 0, "Em Observação": 1, "Pendente": 2}
    df_ativos["_ordem"] = df_ativos["Status"].map(_STATUS_ORDER).fillna(3)
    df_ativos = df_ativos.sort_values(["_ordem", "_dias"], ascending=[True, False])

    st.caption(f"{len(df_ativos)} problema(s) em aberto")

    # Grade de 2 cards por linha
    rows = list(df_ativos.iterrows())
    for i in range(0, len(rows), 2):
        cols = st.columns(2)
        for j, (_, row) in enumerate(rows[i:i + 2]):
            with cols[j]:
                st.markdown(_card_quadro(row, int(row.get("_dias", 0))), unsafe_allow_html=True)

    with st.expander("📖 Legenda de tags"):
        for tag, desc in TAGS.items():
            st.markdown(f"- **{tag}** — {desc}")


# ── Tab 3: Meus Registros (edição própria enquanto Pendente) ──────────────────

def _tab_meus_registros(colab: str):
    st.markdown("""<div style="border-left:4px solid #7c3aed;padding:0.1rem 0 0.1rem 0.9rem;margin:0.9rem 0">
        <span style="font-size:1rem;font-weight:700;color:#1e293b">Meus registros pendentes</span>
        <span style="font-size:0.82rem;color:#64748b;margin-left:0.5rem">
            — editáveis enquanto não classificados pela gestão
        </span>
    </div>""", unsafe_allow_html=True)

    col_r, _ = st.columns([1, 5])
    with col_r:
        if st.button("🔄 Atualizar", key="btn_refresh_meus"):
            carregar_problemas.clear()

    df = carregar_problemas()

    if df.empty or "Colaborador" not in df.columns:
        st.info("📭 Nenhum registro encontrado.")
        return

    mask_pend = df.get("Status", "Pendente") == "Pendente" if "Status" not in df.columns else df["Status"] == "Pendente"
    mask_colab = df["Colaborador"] == colab
    df_meus = df[mask_colab & mask_pend].copy()

    if df_meus.empty:
        st.info("Você não tem problemas pendentes de edição.")
        st.caption("Problemas já classificados pela gestão não podem ser editados.")
        return

    st.caption(f"{len(df_meus)} problema(s) pendente(s)")

    for _, row in df_meus.iterrows():
        pid = str(row.get("ID", "")).strip()
        if not pid:
            continue

        st.markdown(_card_meu_problema(row), unsafe_allow_html=True)

        with st.expander("✏️ Editar este registro"):
            with st.form(key=f"form_edit_{pid}"):
                nova_area = st.selectbox(
                    "Área afetada:",
                    AREAS,
                    index=AREAS.index(row.get("Area")) if row.get("Area") in AREAS else 0,
                )

                col_d, col_i = st.columns(2)
                with col_d:
                    nova_desc = st.text_area(
                        "O que aconteceu?",
                        value=str(row.get("Descricao", "")),
                        height=120,
                    )
                with col_i:
                    novo_imp = st.text_area(
                        "Qual o impacto?",
                        value=str(row.get("Impacto", "")),
                        height=120,
                    )

                c1, c2 = st.columns(2)
                with c1:
                    nova_recorr = st.selectbox(
                        "É recorrente?",
                        RECORRENCIAS,
                        index=RECORRENCIAS.index(row.get("Recorrente")) if row.get("Recorrente") in RECORRENCIAS else 0,
                    )
                with c2:
                    nova_grav = st.selectbox(
                        "Gravidade:",
                        GRAVIDADES,
                        index=GRAVIDADES.index(row.get("Gravidade")) if row.get("Gravidade") in GRAVIDADES else 0,
                        format_func=lambda x: x if x else "— Não informado —",
                    )

                nova_causa = st.text_area("Possível causa:", value=str(row.get("Causa", "")), height=80)
                nova_sug   = st.text_area("Sugestão:", value=str(row.get("Sugestao", "")), height=80)
                nova_ref   = st.text_input("NF / Nº Pedido:", value=str(row.get("Referencia", "")))

                salvo = st.form_submit_button("💾 Salvar alterações", type="primary", use_container_width=True)

            if salvo:
                if not nova_desc.strip():
                    st.error("⚠️ O campo 'O que aconteceu?' é obrigatório.")
                else:
                    ok = atualizar_problema(pid, {
                        "Area":      nova_area,
                        "Descricao": nova_desc,
                        "Impacto":   novo_imp,
                        "Recorrente": nova_recorr,
                        "Gravidade": nova_grav,
                        "Causa":     nova_causa,
                        "Sugestao":  nova_sug,
                        "Referencia": nova_ref,
                    })
                    if ok:
                        st.toast("Registro atualizado!", icon="✅")
                        st.rerun()
                    else:
                        st.error("⚠️ Falha ao salvar. Tente novamente.")


# ── Tab 4: Gestão (Larissa Plácido only) ──────────────────────────────────────

def _form_gestao(row, responsaveis: list, prefix: str):
    problema_id = str(row.get("ID", "")).strip()

    st.caption(
        f"**Colaborador:** {row.get('Colaborador', '—')} &nbsp;|&nbsp; "
        f"**Área:** {row.get('Area', '—')} &nbsp;|&nbsp; "
        f"**Data:** {row.get('Data', '—')} {row.get('Hora', '')}"
    )
    st.markdown(f"**O que aconteceu:** {row.get('Descricao', '')}")
    impacto = str(row.get("Impacto", "")).strip()
    if impacto:
        st.markdown(f"**Impacto:** {impacto}")
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
                "Prioridade", PRIORIDADES, index=idx_prio,
                format_func=lambda x: x if x else "— Não definida —",
            )
        with c4:
            resp_val = str(row.get("Responsavel", ""))
            idx_resp = responsaveis.index(resp_val) if resp_val in responsaveis else 0
            novo_resp = st.selectbox(
                "Responsável pela Análise",
                responsaveis,
                index=idx_resp,
                format_func=lambda x: x if x else "— Não atribuído —",
                help="Quem vai acompanhar, cobrar evolução e prestar contas sobre este problema.",
            )

        novo_resp_trat = st.text_input(
            "Responsável pela Tratativa",
            value=str(row.get("ResponsavelTratativa", "")),
            placeholder="Ex.: Equipe Transportadora / Fulano / Setor de TI",
            help="Quem vai atuar diretamente na resolução — pode ser uma pessoa, setor ou empresa externa.",
        )

        tags_atuais = [t.strip() for t in str(row.get("Tags", "")).split(";") if t.strip() and t.strip() in TAGS]
        novas_tags = st.multiselect(
            "Tags", options=list(TAGS.keys()), default=tags_atuais,
            help=" | ".join(f"**{k}**: {v}" for k, v in TAGS.items()),
        )

        tipo_val = str(row.get("TipoSolucao", ""))
        idx_tipo = TIPO_SOLUCAO.index(tipo_val) if tipo_val in TIPO_SOLUCAO else 0
        novo_tipo = st.selectbox(
            "Tipo de solução", TIPO_SOLUCAO, index=idx_tipo,
            format_func=lambda x: x if x else "— Não definido —",
        )

        nova_acao = st.text_area(
            "Ação tomada", value=str(row.get("AcaoTomada", "")), height=80,
            placeholder="Descreva o que foi feito ou decidido...",
        )

        doc_gerado = st.checkbox(
            "Documento / POP gerado",
            value=str(row.get("DocumentoGerado", "")).upper() == "TRUE",
        )

        salvo = st.form_submit_button("💾 Salvar", type="primary", use_container_width=True)

    if salvo:
        campos = {
            "Titulo":                 novo_titulo,
            "Status":                 novo_status,
            "Prioridade":             nova_prioridade,
            "Responsavel":            novo_resp,
            "ResponsavelTratativa":   novo_resp_trat,
            "Tags":                   "; ".join(novas_tags),
            "TipoSolucao":            novo_tipo,
            "AcaoTomada":             nova_acao,
            "DocumentoGerado":        "TRUE" if doc_gerado else "FALSE",
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

    # ── Triagem ───────────────────────────────────────────────────────────────
    df_pend = df[df["Status"] == "Pendente"].copy()

    st.markdown(
        f'<div style="border-left:4px solid #f59e0b;padding:0.1rem 0 0.1rem 0.9rem;margin:1.2rem 0 0.6rem">'
        f'<span style="font-size:1rem;font-weight:700;color:#1e293b">'
        f'📬 Fila de Triagem — {len(df_pend)} pendente(s)</span></div>',
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

    # ── Em Andamento ──────────────────────────────────────────────────────────
    df_and = df[df["Status"].isin(["Em Análise", "Em Observação"])].copy()
    if "Data" in df_and.columns:
        df_and["_dias"] = df_and["Data"].apply(_dias_aberto)

    st.markdown(
        f'<div style="border-left:4px solid #0369a1;padding:0.1rem 0 0.1rem 0.9rem;margin:1.2rem 0 0.6rem">'
        f'<span style="font-size:1rem;font-weight:700;color:#1e293b">'
        f'🔄 Em Andamento — {len(df_and)} tarefa(s)</span></div>',
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
            resp   = str(row.get("Responsavel", "")).strip() or "—"
            dias   = int(row.get("_dias", 0)) if "_dias" in row else 0
            label  = f"🔄 {titulo} — {resp} — {dias}d — {row.get('Status', '')}"
            with st.expander(label):
                _form_gestao(row, responsaveis, "and")

    # ── Histórico ─────────────────────────────────────────────────────────────
    df_hist = df[df["Status"].isin(["Resolvido", "Descartado"])].copy()

    st.markdown(
        f'<div style="border-left:4px solid #10b981;padding:0.1rem 0 0.1rem 0.9rem;margin:1.2rem 0 0.6rem">'
        f'<span style="font-size:1rem;font-weight:700;color:#1e293b">'
        f'📁 Histórico — {len(df_hist)} registro(s)</span></div>',
        unsafe_allow_html=True,
    )

    if df_hist.empty:
        st.info("Nenhum problema resolvido ou descartado ainda.")
    else:
        cols_hist = [c for c in ["Data", "Area", "Titulo", "Status", "Responsavel", "TipoSolucao", "DocumentoGerado"]
                     if c in df_hist.columns]
        if "Titulo" in df_hist.columns:
            df_hist = df_hist.copy()
            df_hist["Titulo"] = df_hist.apply(
                lambda r: str(r.get("Titulo", "")).strip() or str(r.get("Descricao", ""))[:60],
                axis=1,
            )
        st.dataframe(df_hist[cols_hist].iloc[::-1], use_container_width=True, hide_index=True)

        csv = df_hist.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            "⬇️ Exportar histórico CSV",
            data=csv,
            file_name="historico_problemas.csv",
            mime="text/csv",
        )


# ── Tab 4: Acompanhamento de Tratativas ───────────────────────────────────────

def _tab_acompanhamento(colab: str):
    st.markdown("""<div style="border-left:4px solid #0369a1;padding:0.1rem 0 0.1rem 0.9rem;margin:0.9rem 0">
        <span style="font-size:1rem;font-weight:700;color:#1e293b">Registrar atualização</span>
        <span style="font-size:0.82rem;color:#64748b;margin-left:0.5rem">
            — relate o que está acontecendo no processo de resolução
        </span>
    </div>""", unsafe_allow_html=True)

    df_prob = carregar_problemas()

    if df_prob.empty or "Status" not in df_prob.columns:
        st.info("📭 Nenhum problema ativo para acompanhar.")
        return

    df_ativos = df_prob[~df_prob["Status"].isin(["Resolvido", "Descartado"])].copy()

    if df_ativos.empty:
        st.success("✅ Nenhum problema em aberto no momento. Tudo resolvido!")
        return

    def _label_problema(row) -> str:
        titulo = str(row.get("Titulo", "")).strip() or str(row.get("Descricao", ""))[:60]
        area = str(row.get("Area", ""))
        pid = str(row.get("ID", ""))
        return f"[{pid}] {titulo} — {area}"

    opcoes: dict[str, tuple] = {}
    for _, row in df_ativos.iterrows():
        lbl = _label_problema(row)
        titulo = str(row.get("Titulo", "")).strip() or str(row.get("Descricao", ""))[:80]
        opcoes[lbl] = (str(row.get("ID", "")), titulo)

    opcoes_labels = list(opcoes.keys())
    problema_label = st.selectbox("🔍 Selecione o problema:", opcoes_labels, key="sel_acomp")
    problem_id, problem_titulo = opcoes.get(problema_label, ("", ""))

    st.text_area(
        "📝 O que está acontecendo no processo de resolução?",
        key="atualizacao_acomp",
        height=130,
        placeholder=(
            "Ex.: Aguardando retorno da transportadora. Ligamos em 04/03 e prometeram resposta até amanhã. "
            "Ticket aberto sob nº 98765..."
        ),
    )

    atualizacao = st.session_state.get("atualizacao_acomp", "")

    col_btn, _ = st.columns([3, 1])
    with col_btn:
        st.button(
            "✅ Registrar Atualização",
            key="btn_save_acomp",
            on_click=_callback_salvar_acompanhamento,
            args=(colab, problem_id, problem_titulo),
            disabled=not atualizacao.strip(),
            type="primary",
            use_container_width=True,
        )

    if not atualizacao.strip():
        st.caption("⚠️ Descreva o que está acontecendo antes de registrar.")

    # ── Timeline de atualizações ──────────────────────────────────────────────
    st.markdown("<hr style='margin:1.1rem 0;border-color:#e2e8f0'>", unsafe_allow_html=True)
    st.markdown("""<div style="border-left:4px solid #64748b;padding:0.1rem 0 0.1rem 0.9rem;margin-bottom:0.75rem">
        <span style="font-size:0.95rem;font-weight:700;color:#1e293b">Histórico de atualizações</span>
    </div>""", unsafe_allow_html=True)

    col_r, _ = st.columns([1, 5])
    with col_r:
        if st.button("🔄 Atualizar", key="btn_refresh_acomp"):
            carregar_acompanhamentos.clear()

    df_acomp = carregar_acompanhamentos()

    if df_acomp.empty or "ProblemID" not in df_acomp.columns:
        st.info("📭 Nenhuma atualização registrada ainda para nenhum problema.")
        return

    if not problem_id:
        st.info("Selecione um problema para ver o histórico.")
        return

    df_filtrado = df_acomp[df_acomp["ProblemID"].astype(str) == problem_id].copy()

    if df_filtrado.empty:
        st.info("Nenhuma atualização registrada para este problema ainda. Seja o primeiro!")
        return

    st.caption(f"{len(df_filtrado)} atualização(ões) registrada(s)")

    for _, row in df_filtrado.iloc[::-1].iterrows():
        data = str(row.get("Data", ""))
        hora = str(row.get("Hora", ""))
        colaborador = str(row.get("Colaborador", "")) or "—"
        atualiz = str(row.get("Atualizacao", ""))

        st.markdown(
            f'<div style="background:white;border-radius:10px;padding:0.9rem 1.1rem;'
            f'box-shadow:0 2px 8px -2px rgba(0,0,0,0.07);border-left:4px solid #0369a1;'
            f'margin-bottom:0.6rem">'
            f'<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.4rem">'
            f'<span style="font-weight:700;font-size:0.83rem;color:#0369a1">👤 {colaborador}</span>'
            f'<span style="font-size:0.75rem;color:#94a3b8">{data} {hora}</span>'
            f'</div>'
            f'<p style="margin:0;color:#334155;font-size:0.87rem;line-height:1.5">{atualiz}</p>'
            f'</div>',
            unsafe_allow_html=True,
        )


# ── Página principal ──────────────────────────────────────────────────────────

def pagina_problemas():
    if st.session_state.pop("sucesso_prob", False):
        st.toast("Problema registrado com sucesso!", icon="✅")
    if st.session_state.pop("erro_prob", False):
        st.error("⚠️ Falha ao salvar. Tente novamente.")

    if st.session_state.pop("sucesso_acomp", False):
        st.toast("Atualização registrada com sucesso!", icon="✅")
    if st.session_state.pop("erro_acomp", False):
        st.error("⚠️ Falha ao salvar atualização. Tente novamente.")

    aviso = st.session_state.pop("_aviso_dup_prob", None)
    if aviso is not None:
        st.warning(f"⚠️ Aguarde {aviso}s antes de registrar novamente.")

    aviso_acomp = st.session_state.pop("_aviso_dup_acomp", None)
    if aviso_acomp is not None:
        st.warning(f"⚠️ Aguarde {aviso_acomp}s antes de registrar nova atualização.")

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

    tab_names = ["➕ Registrar Problema", "📊 Quadro Público", "✏️ Meus Registros", "📌 Acompanhamento"]
    if usuario == GESTORA:
        tab_names.append("🛠️ Gestão")

    tabs = st.tabs(tab_names)

    with tabs[0]:
        _tab_registrar(usuario)

    with tabs[1]:
        _tab_quadro_publico()

    with tabs[2]:
        _tab_meus_registros(usuario)

    with tabs[3]:
        _tab_acompanhamento(usuario)

    if len(tabs) > 4:
        with tabs[4]:
            _tab_gestao()
