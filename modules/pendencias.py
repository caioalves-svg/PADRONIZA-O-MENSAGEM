import hashlib
import time

import streamlit as st

from modules.templates import carregar_templates, carregar_listas
from modules.sheets import salvar_registro
from modules.validation import validar_pendencia

_COOLDOWN = 60


def _hash_ticket_p() -> str:
    colab = st.session_state.get("usuario_logado") or st.session_state.get("_colab_p_val", "")
    ped   = st.session_state.get("ped_p", "")
    nf    = st.session_state.get("nf_p", "")
    chave = f"{colab}|{ped}|{nf}"
    return hashlib.md5(chave.encode()).hexdigest()


def _callback_registrar(texto_final: str, colab: str):
    st.session_state["texto_persistente_p"] = texto_final

    hash_atual   = _hash_ticket_p()
    ultimo_hash  = st.session_state.get("_ultimo_hash_p", "")
    ultimo_tempo = st.session_state.get("_ultimo_save_p", 0.0)
    decorrido    = time.time() - ultimo_tempo

    if hash_atual == ultimo_hash and decorrido < _COOLDOWN:
        restante = int(_COOLDOWN - decorrido)
        st.session_state["_aviso_dup_p"] = restante
        return

    if st.session_state.get("_salvando_p"):
        return
    st.session_state["_salvando_p"] = True

    dados = {
        "setor":            "Pend\u00eancia",
        "colaborador":      colab,
        "motivo":           st.session_state.get("msg_p", ""),
        "portal":           st.session_state.get("portal_p", ""),
        "nota_fiscal":      st.session_state.get("nf_p", ""),
        "numero_pedido":    st.session_state.get("ped_p", ""),
        "motivo_crm":       st.session_state.get("crm_p", ""),
        "transportadora":   st.session_state.get("transp_p", "-"),
        "cobranca":         st.session_state.get("cobrar_p", False),
        "celular_cobranca": st.session_state.get("celular_cobr_p", ""),
    }

    sucesso = salvar_registro(dados)
    st.session_state["_salvando_p"] = False

    if sucesso:
        st.session_state["_ultimo_hash_p"] = hash_atual
        st.session_state["_ultimo_save_p"] = time.time()
        st.session_state["sucesso_recente_p"] = True

        for campo in ["cliente_p", "nf_p", "ped_p", "celular_cobr_p"]:
            if campo in st.session_state:
                st.session_state[campo] = ""
        st.session_state["cobrar_p"] = False
    else:
        st.session_state["erro_recente_p"] = True


def _limpar_campos_p():
    for campo in ["cliente_p", "nf_p", "ped_p", "celular_cobr_p"]:
        if campo in st.session_state:
            st.session_state[campo] = ""
    st.session_state["cobrar_p"] = False
    st.session_state.pop("_ultimo_hash_p", None)
    st.session_state.pop("_ultimo_save_p", None)
    st.session_state.pop("texto_persistente_p", None)


def pagina_pendencias():
    if st.session_state.pop("sucesso_recente_p", False):
        st.toast("Registrado e Limpo!", icon="\u2705")
    if st.session_state.pop("erro_recente_p", False):
        st.error("\u26a0\ufe0f Falha ao salvar no Google Sheets. Tente novamente.")

    restante = st.session_state.pop("_aviso_dup_p", None)
    if restante is not None:
        st.warning(
            f"\u26a0\ufe0f **Registro duplicado bloqueado.** Este pedido j\u00e1 foi registrado "
            f"h\u00e1 menos de {restante} segundos. Mude o n\u00famero do pedido ou NF para "
            f"continuar, ou aguarde antes de registrar o mesmo atendimento novamente."
        )

    st.markdown("""
    <div style="background:linear-gradient(135deg,#6d28d9 0%,#7c3aed 50%,#2563eb 100%);
                border-radius:20px;padding:1.75rem 2rem;margin-bottom:1.25rem;color:white">
        <h1 style="margin:0;color:white;font-size:1.9rem;font-weight:800;letter-spacing:-0.5px">
            \U0001f69a Pend\u00eancias Log\u00edsticas
        </h1>
        <p style="margin:0.35rem 0 0;opacity:0.85;font-size:0.9rem">
            Registre ocorr\u00eancias e copie mensagens prontas para o cliente
        </p>
    </div>""", unsafe_allow_html=True)

    listas          = carregar_listas()
    colabs          = listas["colaboradores_pendencias"]
    portais         = listas["lista_portais"]
    transportadoras = listas["lista_transportadoras"]
    motivos_crm     = listas["lista_motivo_crm"]
    modelos         = carregar_templates("pendencias")

    tipo_fluxo = st.radio("Tipo de Registro:", ["Pend\u00eancia", "Atraso", "Devolu\u00e7\u00e3o"], horizontal=True)
    st.markdown("<hr style='margin:0.5rem 0 1rem;border-color:#e2e8f0'>", unsafe_allow_html=True)

    if tipo_fluxo == "Pend\u00eancia":
        st.markdown("""<div style="border-left:4px solid #7c3aed;padding:0.1rem 0 0.1rem 0.9rem;margin-bottom:0.9rem">
            <span style="font-size:1rem;font-weight:700;color:#1e293b">1. Configura\u00e7\u00e3o</span>
        </div>""", unsafe_allow_html=True)

        usuario = st.session_state.get("usuario_logado", "")
        if usuario:
            colab   = usuario
            travado = True
        else:
            travado = False
            colab   = None

        c1, c2, c3 = st.columns(3)
        with c1:
            if travado:
                # [colab] como única opção — exibe sempre o nome correto, sem depender da lista ou cache
                st.selectbox("\U0001f464 Colaborador:", [colab], disabled=True)
            else:
                colab = st.selectbox("\U0001f464 Colaborador:", colabs, key="colab_p")
        with c2:
            nome_cliente = st.text_input("\U0001f464 Nome do Cliente:", key="cliente_p")
        with c3:
            portal = st.selectbox("\U0001f6d2 Portal:", portais, key="portal_p")

        c4, c5, c6, c7 = st.columns(4)
        with c4:
            nota_fiscal   = st.text_input("\U0001f4c4 Nota Fiscal:", key="nf_p")
        with c5:
            numero_pedido = st.text_input("\U0001f4e6 N\u00famero do Pedido:", key="ped_p")
        with c6:
            motivo_crm = st.selectbox("\U0001f4c2 Motivo CRM:", motivos_crm, key="crm_p")
        with c7:
            transp = st.selectbox("\U0001f69b Transportadora:", transportadoras, key="transp_p")

        st.markdown("<hr style='margin:0.75rem 0;border-color:#e2e8f0'>", unsafe_allow_html=True)
        st.markdown("""<div style="border-left:4px solid #2563eb;padding:0.1rem 0 0.1rem 0.9rem;margin-bottom:0.9rem">
            <span style="font-size:1rem;font-weight:700;color:#1e293b">2. Motivo e Visualiza\u00e7\u00e3o</span>
        </div>""", unsafe_allow_html=True)

        opcao = st.selectbox("Selecione o caso:", sorted(modelos.keys()), key="msg_p")

        texto_cru  = modelos[opcao]
        nome_str   = nome_cliente if nome_cliente else "(Nome do cliente)"
        assinatura = colab if "AMAZON" not in portal else ""
        texto_base = (texto_cru
                      .replace("{transportadora}", str(transp))
                      .replace("{colaborador}", assinatura)
                      .replace("{nome_cliente}", nome_str)
                      .replace("(Nome do cliente)", nome_str))

        motivos_sem_texto = [
            "ATENDIMENTO DIGISAC", "2\u00b0 TENTATIVA DE CONTATO", "3\u00b0 TENTATIVA DE CONTATO",
            "REENTREGA", "AGUARDANDO TRANSPORTADORA",
        ]
        if opcao not in motivos_sem_texto:
            ped_str = numero_pedido if numero_pedido else "..."
            frase   = f"O atendimento \u00e9 referente ao seu pedido de n\u00famero {ped_str}..."
            if "\n" in texto_base:
                partes = texto_base.split("\n", 1)
                texto_final = f"{partes[0]}\n\n{frase}\n{partes[1]}"
            else:
                texto_final = f"{frase}\n\n{texto_base}"
        else:
            texto_final = ""

        st.markdown(f'<div class="preview-box">{texto_final}</div>', unsafe_allow_html=True)
        st.write("")

        dados_validar = {
            "colaborador":    colab,
            "nome_cliente":   nome_cliente,
            "portal":         portal,
            "numero_pedido":  numero_pedido,
            "motivo_crm":     motivo_crm,
            "transportadora": transp,
        }
        faltando = validar_pendencia(dados_validar)
        if faltando:
            st.error(f"\u26a0\ufe0f Campos obrigat\u00f3rios: {', '.join(faltando)}")

        hash_atual   = _hash_ticket_p()
        ultimo_hash  = st.session_state.get("_ultimo_hash_p", "")
        ultimo_tempo = st.session_state.get("_ultimo_save_p", 0.0)
        ja_registrado = (
            hash_atual == ultimo_hash
            and bool(numero_pedido or nota_fiscal)
            and (time.time() - ultimo_tempo) < _COOLDOWN
        )
        if ja_registrado:
            restante_btn = int(_COOLDOWN - (time.time() - ultimo_tempo))
            st.info(f"\U0001f512 Pedido j\u00e1 registrado. Altere o pedido/NF ou aguarde {restante_btn}s para re-registrar.")

        st.markdown("<hr style='margin:0.75rem 0;border-color:#e2e8f0'>", unsafe_allow_html=True)
        cobrar = st.checkbox(
            "\U0001f4b0 Direcionar para cobran\u00e7a?",
            key="cobrar_p",
            help="Marque se o cliente recebeu o produto mas j\u00e1 foi reembolsado. "
                 "Os dados preenchidos acima ser\u00e3o registrados automaticamente no controle de cobran\u00e7as.",
        )
        celular_cobr = ""
        if cobrar:
            celular_cobr = st.text_input(
                "\U0001f4f1 Celular do cliente *",
                key="celular_cobr_p",
                placeholder="(11) 99999-9999",
            )
            if not celular_cobr.strip():
                st.warning("\u26a0\ufe0f Informe o celular do cliente para direcionar \u00e0 cobran\u00e7a.")

        faltando_cobr = cobrar and not celular_cobr.strip()

        col_btn1, col_btn2 = st.columns([3, 1])
        with col_btn1:
            st.markdown('<div class="botao-registrar">', unsafe_allow_html=True)
            st.button(
                "\u2705 Registrar e Copiar",
                key="btn_save_pend",
                on_click=_callback_registrar,
                args=(texto_final, colab),
                disabled=bool(faltando) or ja_registrado or faltando_cobr,
            )
            st.markdown("</div>", unsafe_allow_html=True)
        with col_btn2:
            st.button(
                "\U0001f5d1\ufe0f Limpar Campos",
                key="btn_limpar_pend",
                on_click=_limpar_campos_p,
                use_container_width=True,
            )

        if "texto_persistente_p" in st.session_state:
            st.markdown("---")
            st.info("\U0001f4dd \u00daltimo texto registrado (C\u00f3pia Segura):")
            st.code(st.session_state["texto_persistente_p"], language="text")

    elif tipo_fluxo == "Atraso":
        st.subheader("Registro de Atraso")
        usuario_atraso = st.session_state.get("usuario_logado", "")
        with st.form("form_atraso", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                if usuario_atraso:
                    st.selectbox("\U0001f464 Colaborador:", [usuario_atraso], disabled=True)
                    colab = usuario_atraso
                else:
                    colab = st.selectbox("\U0001f464 Colaborador:", colabs)
                nf     = st.text_input("\U0001f4c4 Nota Fiscal:")
                pedido = st.text_input("\U0001f4e6 N\u00famero do Pedido:")
            with c2:
                transp = st.selectbox("\U0001f69b Transportadora:", transportadoras)
                status = st.selectbox("Status:", ["ENTREGUE", "CANCELADO", "COBRADO"])
            submitted = st.form_submit_button("\u2705 Registrar Atraso")
            if submitted:
                salvar_registro({
                    "setor": "Pend\u00eancia", "colaborador": colab,
                    "motivo": f"ATRASO - {status}", "portal": "-",
                    "nota_fiscal": nf, "numero_pedido": pedido,
                    "motivo_crm": "-", "transportadora": transp,
                })
                st.toast("Atraso registrado!", icon="\u2705")

    elif tipo_fluxo == "Devolu\u00e7\u00e3o":
        st.subheader("Registro de Devolu\u00e7\u00e3o")
        usuario_dev = st.session_state.get("usuario_logado", "")
        with st.form("form_devolucao", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                if usuario_dev:
                    st.selectbox("\U0001f464 Colaborador:", [usuario_dev], disabled=True)
                    colab = usuario_dev
                else:
                    colab = st.selectbox("\U0001f464 Colaborador:", colabs)
                nf     = st.text_input("\U0001f4c4 Nota Fiscal:")
                pedido = st.text_input("\U0001f4e6 N\u00famero do Pedido:")
            with c2:
                transp = st.selectbox("\U0001f69b Transportadora:", transportadoras)
                status = st.selectbox("Status:", ["DEVOLVIDO", "COBRADO"])
            submitted = st.form_submit_button("\u2705 Registrar Devolu\u00e7\u00e3o")
            if submitted:
                salvar_registro({
                    "setor": "Pend\u00eancia", "colaborador": colab,
                    "motivo": f"DEVOLU\u00c7\u00c3O - {status}", "portal": "-",
                    "nota_fiscal": nf, "numero_pedido": pedido,
                    "motivo_crm": "-", "transportadora": transp,
                })
                st.toast("Devolu\u00e7\u00e3o registrada!", icon="\u2705")
