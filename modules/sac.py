import hashlib
import time

import streamlit as st

from modules.templates import carregar_templates, carregar_listas
from modules.sheets import salvar_registro
from modules.validation import validar_sac

_COOLDOWN = 60


CAMPOS_EXTRAS: dict[str, list[tuple]] = {
    "SOLICITA\u00c7\u00c3O DE COLETA": [
        ("Endere\u00e7o da coleta (Bairro/Cidade):", "end_coleta_sac", "text", "endereco_resumido"),
    ],
    "ASSIST\u00caNCIA T\u00c9CNICA (DENTRO DOS 7 DIAS)": [
        ("Nome da Fabricante:", "fab_in_7", "text", "fabricante"),
        ("Endere\u00e7o/Telefone/Infos:", "cont_assist_in_7", "area", "contato_assistencia"),
    ],
    "ASSIST\u00caNCIA T\u00c9CNICA (FORA DOS 7 DIAS)": [
        ("Data da Compra:", "data_comp_out_7", "text", "data_compra"),
        ("N\u00famero da NF:", "nf_out_7", "text", "nota_fiscal"),
        ("Link do Posto Autorizado:", "link_out_7", "text", "link_posto"),
    ],
    "C\u00d3DIGO POSTAL (LOG\u00cdSTICA REVERSA)": [
        ("C\u00f3digo de Postagem:", "cod_post_sac", "text", "codigo_postagem"),
    ],
    "C\u00d3DIGO COLETA DOMICILIAR": [
        ("C\u00f3digo de Coleta:", "cod_col_sac", "text", "codigo_coleta"),
    ],
    "CONFIRMA\u00c7\u00c3O DE ENTREGA": [
        ("Transportadora:", "tr_ent_sac_conf", "select_transp", "transportadora"),
        ("Data da Entrega:", "data_ent_sac", "text", "data_entrega"),
    ],
    "CONVERS\u00c3O GLP/GNV": [
        ("Nome do Fabricante:", "fab_glp", "text", "fabricante"),
        ("Site/Contato:", "site_glp", "text", "site_fabricante"),
    ],
    "OFERECER DESCONTO POR AVARIA": [
        ("Valor do reembolso (R$):", "val_desc", "text", "valor_desconto"),
    ],
    "MERCADORIA EM TR\u00c2NSITO": [
        ("Previs\u00e3o de Entrega:", "prev_ent", "text", "previsao_entrega"),
        ("Link de Rastreio:", "link_rast", "text", "link_rastreio"),
        ("Nota Fiscal:", "nf_rast", "text", "nota_fiscal"),
        ("Transportadora:", "tr_trans_sac", "select_transp", "transportadora"),
    ],
    "FISCALIZA\u00c7\u00c3O": [
        ("Transportadora:", "tr_fisc_sac", "select_transp", "transportadora"),
    ],
    "ENTREGA RECUSADA": [
        ("Data/Hor\u00e1rio limite:", "data_limite_recusa", "text", "data_limite"),
    ],
    "PEDIDO CANCELADO (ENTREGUE)": [
        ("Data da Entrega:", "data_entrega_canc_ent", "text", "data_entrega"),
    ],
}

LISTA_LIVRE = [
    "OUTROS", "RECLAME AQUI", "INFORMA\u00c7\u00c3O SOBRE COLETA",
    "INFORMA\u00c7\u00c3O SOBRE ENTREGA", "INFORMA\u00c7\u00c3O SOBRE O PRODUTO",
    "INFORMA\u00c7\u00c3O SOBRE O REEMBOLSO",
]

SCRIPTS_MARTINS = [
    "CANCELAMENTO MARTINS (FRETE)",
    "CANCELAMENTO MARTINS (ESTOQUE)",
    "CANCELAMENTO MARTINS (PRE\u00c7O)",
]

EXCECOES_NF = [
    "SAUDA\u00c7\u00c3O", "AGRADECIMENTO", "AGRADECIMENTO 2", "PR\u00c9-VENDA",
    "BARRAR ENTREGA NA TRANSPORTADORA", "ALTERA\u00c7\u00c3O DE ENDERE\u00c7O (SOLICITA\u00c7\u00c3O DE DADOS)",
    "ESTOQUE FALTANTE", "COMPROVANTE DE ENTREGA (MARTINS)", "PEDIDO AMAZON FBA",
    "BAIXA ERR\u00d4NEA", "COBRAN\u00c7A INDEVIDA", "INFORMA\u00c7\u00c3O EMBALAGEM",
    "RETIRADA DE ENTREGA", "ENCERRAMENTO DE CHAT", "SOLICITA\u00c7\u00c3O DE COLETA",
] + LISTA_LIVRE


def _hash_ticket_s() -> str:
    colab  = st.session_state.get("usuario_logado") or st.session_state.get("_colab_s_val", "")
    ped    = st.session_state.get("ped_s", "")
    nf     = st.session_state.get("nf_s", "")
    motivo = st.session_state.get("msg_s", "")
    chave  = f"{colab}|{ped}|{nf}|{motivo}"
    return hashlib.md5(chave.encode()).hexdigest()


def _callback_registrar(texto_final: str, transp_extra: str, colab: str):
    st.session_state["texto_persistente_s"] = texto_final

    hash_atual   = _hash_ticket_s()
    ultimo_hash  = st.session_state.get("_ultimo_hash_s", "")
    ultimo_tempo = st.session_state.get("_ultimo_save_s", 0.0)
    decorrido    = time.time() - ultimo_tempo

    if hash_atual == ultimo_hash and decorrido < _COOLDOWN:
        restante = int(_COOLDOWN - decorrido)
        st.session_state["_aviso_dup_s"] = restante
        return

    if st.session_state.get("_salvando_s"):
        return
    st.session_state["_salvando_s"] = True

    dados = {
        "setor":            "SAC",
        "colaborador":      colab,
        "motivo":           st.session_state.get("msg_s", ""),
        "portal":           st.session_state.get("portal_s", ""),
        "nota_fiscal":      st.session_state.get("nf_s", ""),
        "numero_pedido":    st.session_state.get("ped_s", ""),
        "motivo_crm":       st.session_state.get("crm_s", ""),
        "transportadora":   transp_extra or "-",
        "cobranca":         st.session_state.get("cobrar_s", False),
        "celular_cobranca": st.session_state.get("celular_cobr_s", ""),
    }

    sucesso = salvar_registro(dados)
    st.session_state["_salvando_s"] = False

    if sucesso:
        st.session_state["_ultimo_hash_s"] = hash_atual
        st.session_state["_ultimo_save_s"] = time.time()
        st.session_state["sucesso_recente_s"] = True

        for campo in ["cliente_s", "nf_s", "ped_s", "celular_cobr_s"]:
            if campo in st.session_state:
                st.session_state[campo] = ""
        st.session_state["cobrar_s"] = False

        for campo in [
            "end_coleta_sac", "fab_in_7", "cont_assist_in_7", "data_comp_out_7",
            "nf_out_7", "link_out_7", "cod_post_sac", "cod_col_sac", "data_ent_sac",
            "fab_glp", "site_glp", "val_desc", "prev_ent", "link_rast", "nf_rast",
            "rua_ins", "cep_ins", "num_ins", "bair_ins", "cid_ins", "uf_ins",
            "comp_ins", "ref_ins", "data_limite_recusa", "data_entrega_canc_ent",
        ]:
            if campo in st.session_state:
                st.session_state[campo] = ""
    else:
        st.session_state["erro_recente_s"] = True


def _limpar_campos_s():
    campos = [
        "cliente_s", "nf_s", "ped_s", "celular_cobr_s",
        "end_coleta_sac", "fab_in_7", "cont_assist_in_7", "data_comp_out_7",
        "nf_out_7", "link_out_7", "cod_post_sac", "cod_col_sac", "data_ent_sac",
        "fab_glp", "site_glp", "val_desc", "prev_ent", "link_rast", "nf_rast",
        "rua_ins", "cep_ins", "num_ins", "bair_ins", "cid_ins", "uf_ins",
        "comp_ins", "ref_ins", "data_limite_recusa", "data_entrega_canc_ent",
        "texto_livre_s",
    ]
    for campo in campos:
        if campo in st.session_state:
            st.session_state[campo] = ""
    st.session_state["cobrar_s"] = False
    st.session_state.pop("_ultimo_hash_s", None)
    st.session_state.pop("_ultimo_save_s", None)
    if "texto_persistente_s" in st.session_state:
        del st.session_state["texto_persistente_s"]


def pagina_sac():
    if st.session_state.pop("sucesso_recente_s", False):
        st.toast("Registrado e Limpo!", icon="\u2705")
    if st.session_state.pop("erro_recente_s", False):
        st.error("\u26a0\ufe0f Falha ao salvar. Tente novamente.")

    restante = st.session_state.pop("_aviso_dup_s", None)
    if restante is not None:
        st.warning(
            f"\u26a0\ufe0f **Registro duplicado bloqueado.** Este atendimento j\u00e1 foi registrado "
            f"h\u00e1 menos de {restante} segundos. Mude o n\u00famero do pedido ou NF para "
            f"continuar, ou aguarde antes de registrar o mesmo atendimento novamente."
        )

    st.markdown("""
    <div style="background:linear-gradient(135deg,#0369a1 0%,#0ea5e9 55%,#059669 100%);
                border-radius:20px;padding:1.75rem 2rem;margin-bottom:1.25rem;color:white">
        <h1 style="margin:0;color:white;font-size:1.9rem;font-weight:800;letter-spacing:-0.5px">
            \U0001f3a7 SAC / Atendimento
        </h1>
        <p style="margin:0.35rem 0 0;opacity:0.85;font-size:0.9rem">
            Gere mensagens padronizadas e registre atendimentos ao cliente
        </p>
    </div>""", unsafe_allow_html=True)

    listas          = carregar_listas()
    colabs          = listas["colaboradores_sac"]
    portais         = listas["lista_portais"]
    transportadoras = listas["lista_transportadoras"]
    motivos_crm     = listas["lista_motivo_crm"]
    modelos         = carregar_templates("sac")

    lista_motivos = sorted([k for k in modelos if k != "OUTROS"])
    lista_motivos.append("OUTROS")

    usuario = st.session_state.get("usuario_logado", "")
    if usuario:
        colab   = usuario
        travado = True
    else:
        travado = False
        colab   = None

    st.markdown("""<div style="border-left:4px solid #0ea5e9;padding:0.1rem 0 0.1rem 0.9rem;margin-bottom:0.9rem">
        <span style="font-size:1rem;font-weight:700;color:#1e293b">1. Configura\u00e7\u00e3o Obrigat\u00f3ria</span>
    </div>""", unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        if travado:
            # [colab] como única opção — garante exibir o nome correto, sem depender da lista ou cache
            st.selectbox("\U0001f464 Colaborador:", [colab], disabled=True)
        else:
            colab = st.selectbox("\U0001f464 Colaborador:", colabs, key="colab_s")
    with c2:
        nome_cliente = st.text_input("\U0001f464 Nome do Cliente:", key="cliente_s")
    with c3:
        portal = st.selectbox("\U0001f6d2 Portal:", portais, key="portal_s")

    c4, c5, c6 = st.columns(3)
    with c4:
        nota_fiscal = st.text_input("\U0001f4c4 Nota Fiscal:", key="nf_s")
    with c5:
        numero_pedido = st.text_input("\U0001f4e6 N\u00famero do Pedido:", key="ped_s")
    with c6:
        motivo_crm = st.selectbox("\U0001f4c2 Motivo CRM:", motivos_crm, key="crm_s")

    st.markdown("---")

    opcao = st.selectbox("\U0001f4ac Qual o motivo do contato?", lista_motivos, key="msg_s")

    dados_extras: dict[str, str] = {}
    transp_extra = ""

    campos_motivo = CAMPOS_EXTRAS.get(opcao, [])
    if campos_motivo:
        st.info(f"\U0001f4cb Dados adicionais para: {opcao}")
        for label, key, tipo, placeholder in campos_motivo:
            if tipo == "text":
                dados_extras[placeholder] = st.text_input(label, key=key)
            elif tipo == "area":
                dados_extras[placeholder] = st.text_area(label, key=key)
            elif tipo == "select_transp":
                val = st.selectbox(label, transportadoras, key=key)
                dados_extras[placeholder] = val
                transp_extra = val

    st.markdown("<hr style='margin:0.75rem 0;border-color:#e2e8f0'>", unsafe_allow_html=True)
    st.markdown("""<div style="border-left:4px solid #059669;padding:0.1rem 0 0.1rem 0.9rem;margin-bottom:0.9rem">
        <span style="font-size:1rem;font-weight:700;color:#1e293b">2. Visualiza\u00e7\u00e3o da Mensagem</span>
    </div>""", unsafe_allow_html=True)

    if opcao in LISTA_LIVRE:
        if opcao == "RECLAME AQUI":
            label_texto = "Digite a resposta do Reclame Aqui:"
        elif "INFORMA\u00c7\u00c3O" in opcao:
            label_texto = f"Detalhes sobre {opcao}:"
        else:
            label_texto = "Digite a mensagem personalizada:"
        texto_base = st.text_area(label_texto, height=200, key="texto_livre_s")
        if texto_base:
            texto_base += f"\n\nEquipe de atendimento Engage Eletro.\n{{colaborador}}"
    else:
        texto_base = modelos.get(opcao, "")

    nome_str = nome_cliente if nome_cliente else "(Nome do cliente)"
    ped_str  = numero_pedido if numero_pedido else "......"
    texto_base = texto_base.replace("(Nome do cliente)", nome_str)

    if opcao in SCRIPTS_MARTINS:
        texto_final = texto_base.replace("{nome_cliente}", nome_str)
    elif opcao == "RETIRADA DE ENTREGA":
        texto_final = texto_base.replace("{numero_pedido}", ped_str).replace("(Nome do cliente)", nome_str)
    elif opcao == "SOLICITA\u00c7\u00c3O DE COLETA":
        end_res = dados_extras.get("endereco_resumido", "................")
        texto_final = (texto_base
                       .replace("{numero_pedido}", ped_str)
                       .replace("{endereco_resumido}", end_res or "................"))
    elif opcao == "ENCERRAMENTO DE CHAT":
        texto_final = texto_base
    elif opcao == "ESTOQUE FALTANTE":
        texto_final = texto_base.replace("{portal}", str(portal))
    elif opcao == "COMPROVANTE DE ENTREGA (MARTINS)":
        texto_final = ""
    elif opcao == "BARRAR ENTREGA NA TRANSPORTADORA":
        corpo = modelos["BARRAR ENTREGA NA TRANSPORTADORA"].replace("Ol\u00e1, (Nome do cliente)!", "").strip()
        texto_final = f"Ol\u00e1, {nome_str}!\nO atendimento \u00e9 referente ao seu pedido de n\u00famero {ped_str}\n\n{corpo}"
    elif opcao == "ALTERA\u00c7\u00c3O DE ENDERE\u00c7O (SOLICITA\u00c7\u00c3O DE DADOS)":
        corpo = modelos["ALTERA\u00c7\u00c3O DE ENDERE\u00c7O (SOLICITA\u00c7\u00c3O DE DADOS)"].replace("Ol\u00e1, (Nome do cliente)!", "").strip()
        texto_final = f"Ol\u00e1, {nome_str}!\nO atendimento \u00e9 referente ao seu pedido de n\u00famero {ped_str}\n\n{corpo}"
    elif opcao in EXCECOES_NF or opcao in LISTA_LIVRE:
        texto_final = texto_base
    else:
        frase = f"O atendimento \u00e9 referente ao seu pedido de n\u00famero {ped_str}..."
        if "\n" in texto_base:
            partes = texto_base.split("\n", 1)
            texto_final = f"{partes[0]}\n\n{frase}\n{partes[1]}"
        else:
            texto_final = f"{frase}\n\n{texto_base}"

    assinatura  = colab if "AMAZON" not in portal else ""
    texto_final = texto_final.replace("{colaborador}", assinatura)
    for chave, valor in dados_extras.items():
        texto_final = texto_final.replace(f"{{{chave}}}", valor if valor else "................")

    st.markdown(f'<div class="preview-box">{texto_final}</div>', unsafe_allow_html=True)
    st.write("")

    dados_validar = {
        "colaborador": colab,
        "nome_cliente": nome_cliente,
        "portal": portal,
        "motivo": opcao,
        "motivo_crm": motivo_crm,
        **dados_extras,
    }
    faltando = validar_sac(dados_validar, opcao)
    if faltando:
        st.error(f"\u26a0\ufe0f Campos obrigat\u00f3rios: {', '.join(faltando)}")

    hash_atual    = _hash_ticket_s()
    ultimo_hash   = st.session_state.get("_ultimo_hash_s", "")
    ultimo_tempo  = st.session_state.get("_ultimo_save_s", 0.0)
    ja_registrado = (
        hash_atual == ultimo_hash
        and bool(numero_pedido or nota_fiscal)
        and (time.time() - ultimo_tempo) < _COOLDOWN
    )
    if ja_registrado:
        restante_btn = int(_COOLDOWN - (time.time() - ultimo_tempo))
        st.info(f"\U0001f512 Atendimento j\u00e1 registrado. Altere o pedido/NF ou aguarde {restante_btn}s para re-registrar.")

    st.markdown("<hr style='margin:0.75rem 0;border-color:#e2e8f0'>", unsafe_allow_html=True)
    cobrar = st.checkbox(
        "\U0001f4b0 Direcionar para cobran\u00e7a?",
        key="cobrar_s",
        help="Marque se o cliente recebeu o produto mas j\u00e1 foi reembolsado. "
             "Os dados preenchidos acima ser\u00e3o registrados automaticamente no controle de cobran\u00e7as.",
    )
    celular_cobr = ""
    if cobrar:
        celular_cobr = st.text_input(
            "\U0001f4f1 Celular do cliente *",
            key="celular_cobr_s",
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
            key="btn_save_sac",
            on_click=_callback_registrar,
            args=(texto_final, transp_extra, colab),
            disabled=bool(faltando) or ja_registrado or faltando_cobr,
        )
        st.markdown("</div>", unsafe_allow_html=True)
    with col_btn2:
        st.button(
            "\U0001f5d1\ufe0f Limpar Campos",
            key="btn_limpar_sac",
            on_click=_limpar_campos_s,
            use_container_width=True,
        )

    if "texto_persistente_s" in st.session_state:
        st.markdown("---")
        st.info("\U0001f4dd \u00daltimo texto registrado (C\u00f3pia Segura):")
        st.code(st.session_state["texto_persistente_s"], language="text")
