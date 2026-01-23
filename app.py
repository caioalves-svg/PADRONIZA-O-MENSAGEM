import streamlit as st

# --- CONFIGURAÇÃO INICIAL DA PÁGINA ---
st.set_page_config(page_title="Sistema Integrado", page_icon="🏢", layout="wide")

# --- DADOS GERAIS (Compartilhados) ---
# Se os atendentes forem os mesmos para os dois setores, deixe aqui.
# Se forem diferentes, mova para dentro das funções específicas.
lista_colaboradores = sorted([
    "Ana", "Mariana", "Gabriela", "Layra", 
    "Maria Eduarda", "Akisia", "Marcelly", "Camilla"
])

lista_transportadoras = sorted([
    "4ELOS", "ATUAL", "BRASIL WEB", "FAVORITA", "FRONTLOG", 
    "GENEROSO", "JADLOG", "LOGAN", "MMA", "PAJUÇARA", 
    "PATRUS", "REBOUÇAS", "REDE SUL", "RIO EXPRESS", 
    "TJB", "TOTAL", "TRILOG"
])

# --- FUNÇÃO 1: PÁGINA DE PENDÊNCIAS (O que já fizemos) ---
def pagina_pendencias():
    st.header("🚚 Setor de Pendências / Logística")
    st.markdown("---")

    # Dicionário de Mensagens de Pendências
    modelos_pendencias = {
        "Ausente": """Olá, prezado cliente! Tudo bem? Esperamos que sim!\n\nA transportadora {transportadora} tentou realizar a entrega de sua mercadoria no endereço cadastrado, porém, o responsável pelo recebimento estava ausente.\n\nPara solicitarmos uma nova tentativa de entrega à transportadora, poderia por gentileza, nos confirmar dados abaixo?\n\nRua:\nNúmero:\nBairro:\nCEP:\nCidade:\nEstado:\nPonto de Referência:\nRecebedor:\nTelefone:\n\nApós a confirmação dos dados acima, iremos solicitar que a transportadora realize uma nova tentativa de entrega que irá ocorrer no prazo de até 3 a 5 dias úteis. Caso não tenhamos retorno, o produto será devolvido ao nosso Centro de Distribuição e seguiremos com o cancelamento da compra.\n\nQualquer dúvida, estamos à disposição!\n\nAtenciosamente,\n{colaborador}""",
        "Solicitação de Contato": """Olá, prezado cliente! Tudo bem? Esperamos que sim!\n\nPara facilitar a entrega da sua mercadoria e não ter desencontros com a transportadora {transportadora}, o senhor pode por gentileza nos enviar um número de telefone ativo para alinharmos a entrega?\n\nAguardo o retorno!\n\nAtenciosamente,\n{colaborador}""",
        "Endereço Não Localizado": """Olá, prezado cliente! Tudo bem? Esperamos que sim!\n\nA transportadora {transportadora} tentou realizar a entrega de sua mercadoria, porém, não localizou o endereço.\n\nPara solicitarmos uma nova tentativa de entrega à transportadora, poderia por gentileza, nos confirmar dados abaixo:\n\nRua:\nNúmero:\nBairro:\nCEP:\nCidade:\nEstado:\nPonto de Referência:\nRecebedor:\nTelefone:\n\nApós a confirmação dos dados acima, iremos solicitar que a transportadora realize uma nova tentativa de entrega que irá ocorrer no prazo de até 3 a 5 dias úteis. Caso não tenhamos retorno, o produto será devolvido ao nosso Centro de Distribuição e seguiremos com o cancelamento da compra.\n\nAtenciosamente,\n{colaborador}""",
        "Área de Risco": """Olá, prezado cliente! Tudo bem? Espero que sim!\n\nA transportadora {transportadora}, informou que está com dificuldades para realizar a entrega no endereço cadastrado no portal. Dessa forma, peço por gentileza que nos informe um endereço alternativo e também telefones ativos para melhor comunicação.\n\nCaso não possua um outro endereço, sua mercadoria ficará disponível para retirada da base da transportadora.\n\nQualquer dúvida me coloco à disposição para ajudá-lo!\n\nAtenciosamente,\n{colaborador}""",
        "Extravio / Avaria": """Olá, prezado cliente! Tudo bem? Espero que sim!\n\nInfelizmente fomos informados pela transportadora {transportadora} que sua mercadoria foi furtada/avariada em transporte. Antes de tudo, pedimos desculpas pelo ocorrido e por todo transtorno causado.\n\nGostaríamos de saber se o senhor aceita o envio de uma nova mercadoria? O prazo para entrega é de 5 a 7 dias úteis, podendo ocorrer antes.\n\nNovamente, pedimos desculpas. Qualquer dúvida me coloco à disposição para ajudá-lo!\n\nAtenciosamente,\n{colaborador}""",
        "Recusa de Entrega": """Prezado cliente,\n\nA transportadora {transportadora} informou que a entrega foi recusada. Houve algum problema com a apresentação da carga? O senhor deseja o cancelamento da compra?\n\nCaso não tenhamos retorno e o produto seja devolvido ao nosso estoque, seguiremos com o cancelamento da compra.\n\nQualquer dúvida me coloco à disposição para ajudá-lo!\n\nAtenciosamente,\n{colaborador}""",
        "Solicitação de Barramento": """Olá, prezado cliente! Tudo bem? Esperamos que sim!\n\nSolicitamos à transportadora {transportadora} que barre a entrega da sua mercadoria. Caso tentem realizar a entrega, gentileza recusar o recebimento.\n\nAssim que a mercadoria der entrada em nosso estoque, liberamos o estorno.\n\nAtenciosamente,\n{colaborador}""",
        "Garantia de A a Z (Amazon)": """Olá, prezado cliente! Tudo bem? Esperamos que sim!\n\nDiante da abertura da Garantia A a Z, solicitamos à transportadora {transportadora} responsável que barre a entrega e aguardaremos a confirmação da suspensão da entrega, a fim de possibilitar a liberação do reembolso pela plataforma.\n\nAtenciosamente,\n{colaborador}""",
        "Em caso de Reembolso": """Olá, prezado cliente! Tudo bem? Esperamos que sim!\n\nO cancelamento foi liberado conforme solicitado. O reembolso é realizado de acordo com a forma de pagamento da compra:\n\nPara pagamentos com boleto, o reembolso será feito na conta bancária especificada pelo cliente ou como um vale-presente. Se todos os dados da sua conta bancária estiverem corretos, o reembolso pode levar até 3 dias úteis para constar na conta.\n\nCaso você tenha pago com cartão de crédito, dependendo da data de fechamento e vencimento do seu cartão, o reembolso pode levar de uma a duas faturas.\n\nPara pagamento em PIX, o reembolso será realizado na conta PIX em um dia útil.\n\nAtenciosamente,\n{colaborador}""",
        "Mercadoria sem Estoque": """Olá, prezado cliente! Tudo bem? Esperamos que sim!\n\nHouve um erro no sistema que vendeu um item a mais e o lojista não possui a mercadoria disponível em estoque no momento. Verificamos com o nosso fornecedor, e infelizmente não tem a previsão de entrega de um novo lote.\n\nPedimos desculpas pelo transtorno causado.\n\nGostaríamos de saber se podemos seguir com o cancelamento do pedido para que a loja da compra possa realizar o estorno total.\n\nAtenciosamente,\n{colaborador}""",
        "Endereço em Zona Rural": """Olá, prezado cliente! Tudo bem? Esperamos que sim!\n\nA transportadora {transportadora} nos informou que está com dificuldades para realizar a entrega no endereço cadastrado no portal.\n\nPeço por gentileza que nos informe um endereço alternativo e também telefones ativos para melhor comunicação. Caso o senhor não possua um outro endereço, sua mercadoria ficará disponível para retirada a base da transportadora.\n\nAtenciosamente,\n{colaborador}""",
        "Reenvio de Produto": """Olá, prezado cliente! Tudo bem? Esperamos que sim!\n\nConforme solicitado, realizamos o envio de um novo produto ao senhor. Em até 48h você terá acesso a sua nova nota fiscal e poderá acompanhar os passos de sua entrega:\n\nLink: https://ssw.inf.br/2/rastreamento_pf?\n(Necessário inserir o CPF)\n\nNovamente peço desculpas por todo transtorno causado.\n\nAtenciosamente,\n{colaborador}"""
    }

    col1, col2 = st.columns([1, 2])
    with col1:
        st.info("Configuração da Mensagem")
        colab_selecionado = st.selectbox("👤 Colaborador:", lista_colaboradores, key="colab_pend")
        transp_selecionada = st.selectbox("🚛 Transportadora:", lista_transportadoras, key="transp_pend")

    with col2:
        tipo_mensagem = st.selectbox("Selecione o motivo (Pendências):", list(modelos_pendencias.keys()))
        texto_cru = modelos_pendencias[tipo_mensagem]
        texto_final = texto_cru.replace("{transportadora}", transp_selecionada)
        texto_final = texto_final.replace("{colaborador}", colab_selecionado)
        st.text_area("Copie o texto abaixo:", value=texto_final, height=400)
        if st.button("Confirmar Cópia", key="btn_pend"):
            st.success("Texto pronto para cópia!")

# --- FUNÇÃO 2: PÁGINA DE SAC (Nova) ---
def pagina_sac():
    st.header("🎧 Setor de SAC / Atendimento")
    st.markdown("---")
    
    # Dicionário de Mensagens do SAC (Adicione suas mensagens aqui depois!)
    modelos_sac = {
        "Boas Vindas": """Olá, tudo bem?\n\nMeu nome é {colaborador}. Como posso te ajudar hoje?""",
        "Dúvida de Rastreio": """Olá! O seu pedido está sendo transportado pela {transportadora}.\n\nVocê pode acompanhar pelo link de rastreio oficial.\n\nAtenciosamente,\n{colaborador}"""
    }

    col1, col2 = st.columns([1, 2])
    with col1:
        st.info("Configuração da Mensagem")
        # Se no SAC não precisar de transportadora, você pode remover esse selectbox
        colab_selecionado = st.selectbox("👤 Atendente SAC:", lista_colaboradores, key="colab_sac")
        transp_selecionada = st.selectbox("🚛 Transportadora (se houver):", lista_transportadoras, key="transp_sac")

    with col2:
        tipo_mensagem = st.selectbox("Selecione o motivo (SAC):", list(modelos_sac.keys()))
        texto_cru = modelos_sac[tipo_mensagem]
        texto_final = texto_cru.replace("{transportadora}", transp_selecionada)
        texto_final = texto_final.replace("{colaborador}", colab_selecionado)
        st.text_area("Copie o texto abaixo:", value=texto_final, height=400)
        if st.button("Confirmar Cópia", key="btn_sac"):
            st.success("Texto pronto para cópia!")

# --- MENU LATERAL (SIDEBAR) ---
st.sidebar.title("Navegação")
st.sidebar.markdown("Selecione o departamento:")

# O selectbox lateral define qual função vamos chamar
pagina_escolhida = st.sidebar.radio(
    "Ir para:",
    ("Pendências Logísticas", "SAC / Atendimento")
)

# --- CONTROLE DE PÁGINAS ---
if pagina_escolhida == "Pendências Logísticas":
    pagina_pendencias()
elif pagina_escolhida == "SAC / Atendimento":
    pagina_sac()

# Rodapé simples na barra lateral
st.sidebar.markdown("---")
st.sidebar.caption("Desenvolvido para agilizar o atendimento.")
