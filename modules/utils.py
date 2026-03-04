import streamlit as st


def botao_copiar(texto: str, key_suffix: str = "") -> None:
    """Renderiza um botão HTML que copia o texto para a área de transferência via JS."""
    if not texto.strip():
        return

    texto_js = (
        texto
        .replace("\\", "\\\\")
        .replace("`", "\\`")
        .replace("${", "\\${")
    )

    btn_id = f"btn_cp_{key_suffix}"

    st.components.v1.html(
        f"""
        <button id="{btn_id}" onclick="
          var btn = document.getElementById('{btn_id}');
          navigator.clipboard.writeText(`{texto_js}`)
            .then(function() {{
              btn.innerHTML = '✅&nbsp; Copiado!';
              btn.style.background = '#059669';
              setTimeout(function() {{
                btn.innerHTML = '📋&nbsp; Copiar mensagem';
                btn.style.background = '#2563eb';
              }}, 2500);
            }})
            .catch(function() {{
              btn.innerHTML = '⚠️&nbsp; Copie o texto acima manualmente';
              btn.style.background = '#d97706';
            }});
        " style="width:100%;background:#2563eb;color:white;border:none;border-radius:8px;
                 padding:0.6rem 1rem;font-size:0.9rem;font-weight:700;cursor:pointer;
                 letter-spacing:0.01em;transition:background 0.2s ease">
          📋&nbsp; Copiar mensagem
        </button>
        """,
        height=52,
        scrolling=False,
    )
