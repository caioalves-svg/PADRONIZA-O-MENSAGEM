import io
from datetime import date, timedelta

import pandas as pd
import streamlit as st

from modules.sheets import carregar_historico

_PAGE_SIZE = 100


def _exportar_excel(df: pd.DataFrame) -> bytes:
    buffer = io.BytesIO()
    df_exp = df.copy()
    for col in ["Nota_Fiscal", "Numero_Pedido"]:
        if col in df_exp.columns:
            df_exp[col] = df_exp[col].astype(str)
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df_exp.to_excel(writer, sheet_name="Histórico", index=False)
        total = len(df_exp)
        sac  = int((df_exp["Setor"] == "SAC").sum())       if "Setor" in df_exp.columns else 0
        pend = int((df_exp["Setor"] == "Pendência").sum()) if "Setor" in df_exp.columns else 0
        pd.DataFrame({
            "Métrica": ["Total", "SAC", "Pendências"],
            "Valor":   [total, sac, pend],
        }).to_excel(writer, sheet_name="Resumo", index=False)
    return buffer.getvalue()


def _pill(label: str, cor: str, bg: str) -> str:
    return (
        f'<span style="background:{bg};color:{cor};padding:0.15rem 0.65rem;'
        f'border-radius:99px;font-size:0.75rem;font-weight:700;'
        f'border:1px solid {cor}33;white-space:nowrap">{label}</span>'
    )


def _limpar_filtros_hist():
    for k in ["busca_hist", "setor_hist", "colab_hist", "hist_page"]:
        st.session_state.pop(k, None)


def pagina_historico():
    st.markdown(
        '<div style="background:linear-gradient(135deg,#0f172a 0%,#1e3a5f 60%,#0369a1 100%);'
        'border-radius:20px;padding:1.75rem 2rem;margin-bottom:1.25rem;color:white">'
        '<h1 style="margin:0;color:white;font-size:1.9rem;font-weight:800;letter-spacing:-0.5px">'
        '📂 Histórico de Atendimentos'
        '</h1>'
        '<p style="margin:0.35rem 0 0;opacity:0.8;font-size:0.9rem">'
        'Consulte, filtre e exporte os registros da base'
        '</p>'
        '</div>',
        unsafe_allow_html=True,
    )

    # ── Carrega dados (cache próprio de 10 min, independente do Dashboard) ─────
    col_r, _ = st.columns([1, 7])
    with col_r:
        if st.button("🔄 Atualizar", key="btn_refresh_hist", type="secondary"):
            carregar_historico.clear()
            st.session_state.pop("hist_page", None)

    with st.spinner("Carregando base..."):
        df_raw = carregar_historico()

    if df_raw.empty:
        st.warning("⚠️ Sem dados disponíveis. Verifique a conexão com o Google Sheets.")
        return

    df_raw = df_raw.copy()
    df_raw["_data_dt"] = pd.to_datetime(df_raw["Data"], format="%d/%m/%Y", errors="coerce")

    d_min = df_raw["_data_dt"].min().date()
    d_max = df_raw["_data_dt"].max().date()
    d_ini_padrao = max(d_min, d_max - timedelta(days=30))   # padrão: últimos 30 dias

    colabs_lista  = sorted(df_raw["Colaborador"].dropna().unique().tolist()) if "Colaborador" in df_raw.columns else []
    setores_lista = sorted(df_raw["Setor"].dropna().unique().tolist())       if "Setor"        in df_raw.columns else []

    # ── Filtros ────────────────────────────────────────────────────────────────
    st.markdown(
        '<div style="border-left:4px solid #0369a1;padding:0.1rem 0 0.1rem 0.9rem;margin-bottom:0.9rem">'
        '<span style="font-size:1rem;font-weight:700;color:#1e293b">Filtros</span>'
        '</div>',
        unsafe_allow_html=True,
    )

    busca = st.text_input(
        "🔍 Buscar por NF, número do pedido ou colaborador:",
        placeholder="Ex: 123456 ou PED-001 ou Ana",
        key="busca_hist",
    )

    c1, c2, c3, c4, c5 = st.columns([2, 2, 2, 2, 1])
    with c1:
        data_ini = st.date_input("De:", value=d_ini_padrao, format="DD/MM/YYYY", key="di_hist")
    with c2:
        data_fim = st.date_input("Até:", value=d_max, format="DD/MM/YYYY", key="df_hist")
    with c3:
        setor_sel = st.selectbox("Setor:", ["Todos"] + setores_lista, key="setor_hist")
    with c4:
        colab_sel = st.selectbox("Colaborador:", ["Todos"] + colabs_lista, key="colab_hist")
    with c5:
        st.markdown("<div style='margin-top:1.75rem'>", unsafe_allow_html=True)
        st.button("↺ Limpar", key="btn_limpar_hist", on_click=_limpar_filtros_hist,
                  type="secondary", use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # ── Aplica filtros ─────────────────────────────────────────────────────────
    df = df_raw.copy()

    if busca.strip():
        # Busca varre toda a base (ignora período)
        cols_b = [c for c in ["Nota_Fiscal", "Numero_Pedido", "Colaborador", "Motivo"] if c in df.columns]
        mask_b = df[cols_b].astype(str).apply(
            lambda col: col.str.contains(busca.strip(), case=False, na=False)
        ).any(axis=1)
        df = df[mask_b]
    else:
        df = df[
            (df["_data_dt"].dt.date >= data_ini) &
            (df["_data_dt"].dt.date <= data_fim)
        ]

    if setor_sel != "Todos" and "Setor" in df.columns:
        df = df[df["Setor"] == setor_sel]
    if colab_sel != "Todos" and "Colaborador" in df.columns:
        df = df[df["Colaborador"] == colab_sel]

    df = df.sort_values(["_data_dt", "Hora"], ascending=False)
    total = len(df)

    # ── Barra de estatísticas ──────────────────────────────────────────────────
    sac  = int((df["Setor"] == "SAC").sum())       if "Setor" in df.columns else 0
    pend = int((df["Setor"] == "Pendência").sum()) if "Setor" in df.columns else 0

    if busca.strip():
        ctx = f'busca: <strong>"{busca.strip()}"</strong>'
    else:
        ctx = (
            f"período: <strong>{data_ini.strftime('%d/%m/%Y')}"
            f" → {data_fim.strftime('%d/%m/%Y')}</strong>"
        )

    st.markdown(
        f'<div style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:10px;'
        f'padding:0.65rem 1rem;margin:0.75rem 0 0.5rem;display:flex;align-items:center;'
        f'gap:0.75rem;flex-wrap:wrap">'
        f'<span style="font-size:0.85rem;color:#64748b">Exibindo {ctx}</span>'
        f'<span style="color:#cbd5e1">|</span>'
        f'{_pill(f"{total} registros", "#0369a1", "#eff6ff")}'
        f'{_pill(f"SAC: {sac}", "#2563eb", "#eff6ff")}'
        f'{_pill(f"Pendências: {pend}", "#7c3aed", "#faf5ff")}'
        f'</div>',
        unsafe_allow_html=True,
    )

    if total == 0:
        st.info("📭 Nenhum registro encontrado com os filtros aplicados.")
        return

    # ── Paginação ──────────────────────────────────────────────────────────────
    n_pages = max(1, -(-total // _PAGE_SIZE))   # ceil division
    page    = min(st.session_state.get("hist_page", 0), n_pages - 1)

    df_show = df.drop(columns=["_data_dt"], errors="ignore")
    df_page = df_show.iloc[page * _PAGE_SIZE : (page + 1) * _PAGE_SIZE]

    st.data_editor(
        df_page,
        use_container_width=True,
        hide_index=True,
        disabled=True,
        height=min(520, 38 + len(df_page) * 35),
    )

    # Controles de página
    if n_pages > 1:
        pc1, pc2, pc3 = st.columns([1, 3, 1])
        with pc1:
            if st.button("← Anterior", disabled=page == 0, key="hist_prev", type="secondary"):
                st.session_state["hist_page"] = page - 1
                st.rerun()
        with pc2:
            st.markdown(
                f'<p style="text-align:center;font-size:0.85rem;color:#64748b;margin:0.5rem 0">'
                f'Página {page + 1} de {n_pages} '
                f'({page * _PAGE_SIZE + 1}–{min((page + 1) * _PAGE_SIZE, total)} de {total})'
                f'</p>',
                unsafe_allow_html=True,
            )
        with pc3:
            if st.button("Próxima →", disabled=page >= n_pages - 1, key="hist_next", type="secondary"):
                st.session_state["hist_page"] = page + 1
                st.rerun()

    # ── Exportação (exporta tudo filtrado, não só a página) ────────────────────
    st.markdown("<div style='margin-top:0.9rem'></div>", unsafe_allow_html=True)
    nome_base = f"historico_{busca.strip() or data_ini.strftime('%d%m%Y') + '-' + data_fim.strftime('%d%m%Y')}"
    csv = df_show.to_csv(index=False, sep=";", encoding="utf-8-sig").encode("utf-8-sig")

    col_e1, col_e2, col_e3 = st.columns([1, 1, 4])
    with col_e1:
        st.download_button(
            "⬇️ Exportar CSV",
            data=csv,
            file_name=f"{nome_base}.csv",
            mime="text/csv",
        )
    with col_e2:
        try:
            excel = _exportar_excel(df_show)
            st.download_button(
                "📊 Exportar Excel",
                data=excel,
                file_name=f"{nome_base}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
        except Exception:
            pass
