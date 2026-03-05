import io

import pandas as pd
import streamlit as st

from modules.sheets import carregar_dados_dashboard


def pagina_cobranca():
    st.markdown("""
    <div style="background:linear-gradient(135deg,#059669 0%,#047857 50%,#065f46 100%);
                border-radius:20px;padding:1.75rem 2rem;margin-bottom:1.25rem;color:white">
        <h1 style="margin:0;color:white;font-size:1.9rem;font-weight:800;letter-spacing:-0.5px">
            \U0001f4b0 Controle de Cobran\u00e7as
        </h1>
        <p style="margin:0.35rem 0 0;opacity:0.85;font-size:0.9rem">
            Clientes direcionados para cobran\u00e7a \u2014 produto entregue e reembolsado
        </p>
    </div>""", unsafe_allow_html=True)

    col_atualizar, _ = st.columns([1, 5])
    with col_atualizar:
        if st.button("\U0001f504 Atualizar dados", type="secondary"):
            carregar_dados_dashboard.clear()
            st.rerun()

    df = carregar_dados_dashboard()

    if df.empty or "Cobranca" not in df.columns:
        st.info("Nenhum registro de cobran\u00e7a encontrado. Certifique-se de que a coluna 'Cobranca' existe na planilha.")
        return

    df_cob = df[df["Cobranca"].astype(str).str.upper() == "TRUE"].copy()

    if df_cob.empty:
        st.info("Nenhum atendimento marcado para cobran\u00e7a ainda.")
        return

    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        if "Colaborador" in df_cob.columns:
            colaboradores = ["Todos"] + sorted(df_cob["Colaborador"].dropna().unique().tolist())
            filtro_colab = st.selectbox("\U0001f464 Colaborador:", colaboradores)
        else:
            filtro_colab = "Todos"
    with col_f2:
        if "Portal" in df_cob.columns:
            portais = ["Todos"] + sorted(df_cob["Portal"].dropna().unique().tolist())
            filtro_portal = st.selectbox("\U0001f6d2 Portal:", portais)
        else:
            filtro_portal = "Todos"
    with col_f3:
        busca = st.text_input("\U0001f50d Buscar por NF ou Pedido:", placeholder="Digite para filtrar...")

    df_filtrado = df_cob.copy()
    if filtro_colab != "Todos":
        df_filtrado = df_filtrado[df_filtrado["Colaborador"] == filtro_colab]
    if filtro_portal != "Todos":
        df_filtrado = df_filtrado[df_filtrado["Portal"] == filtro_portal]
    if busca.strip():
        mask = pd.Series(False, index=df_filtrado.index)
        for col in ["Nota_Fiscal", "Numero_Pedido"]:
            if col in df_filtrado.columns:
                mask |= df_filtrado[col].astype(str).str.contains(busca.strip(), case=False, na=False)
        df_filtrado = df_filtrado[mask]

    colunas_exibir = [c for c in ["Data", "Colaborador", "Setor", "Portal", "Nota_Fiscal",
                                   "Numero_Pedido", "Motivo_CRM", "Celular_Cobranca"] if c in df_filtrado.columns]

    st.markdown(f"**{len(df_filtrado)} registro(s)** encontrado(s)")
    st.dataframe(df_filtrado[colunas_exibir], use_container_width=True, height=400)

    if not df_filtrado.empty:
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            df_filtrado[colunas_exibir].to_excel(writer, sheet_name="Cobran\u00e7as", index=False)
        st.download_button(
            label="\U0001f4e5 Exportar Excel",
            data=buffer.getvalue(),
            file_name="cobrancas_engage.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
