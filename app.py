import streamlit as st

# Configuração da página
st.set_page_config(page_title="Gerador de Mensagens SAC", page_icon="📦", layout="wide")

st.title("📦 Gerador de Mensagens SAC")
st.markdown("Selecione os dados abaixo. O sistema preenche apenas o que for necessário para cada mensagem.")

st.divider()

# --- DADOS (Listas e Dicionários) ---

lista_transportadoras = sorted([
    "4ELOS", "ATUAL", "BRASIL WEB", "FAVORITA", "FRONTLOG", 
    "GENEROSO", "JADLOG", "LOGAN", "MMA", "PAJUÇARA", 
    "PATRUS", "REBOUÇAS", "REDE SUL", "RIO EXPRESS", 
    "TJB", "TOTAL", "TRILOG"
])

lista_colaboradores = sorted([
    "Ana", "Mariana", "Gabriela", "Layra", 
    "Maria Eduarda", "Akisia", "Marcelly", "Camilla"
])

# Dicionário de Mensagens
# Usamos {transportadora} e {colaborador} como marcadores para substituição
modelos = {
    "Ausente": 
"""Olá, prezado cliente! Tudo bem? Esperamos que sim!

A transportadora {transportadora} tentou realizar a entrega de sua mercadoria no endereço cadastrado, porém, o responsável pelo recebimento estava ausente.

Para solicitarmos uma nova tentativa de entrega à transportadora, poderia por gentileza, nos confirmar dados abaixo?

Rua:
Número:
Bairro:
CEP:
Cidade:
Estado:
Ponto de Referência:
Recebedor:
Telefone:

Após a confirmação dos dados acima, iremos solicitar que a transportadora realize uma nova tentativa de entrega que irá ocorrer no prazo de até 3 a 5 dias úteis. Caso não tenhamos retorno, o produto será devolvido ao nosso Centro de Distribuição e seguiremos com o cancelamento da compra.

Qualquer dúvida, estamos à disposição!

Atenciosamente,
{colaborador}""",

    "Solicitação de Contato":
"""Olá, prezado cliente! Tudo bem? Esperamos que sim!

Para facilitar a entrega da sua mercadoria e não ter desencontros com a transportadora {transportadora}, o senhor pode por gentileza nos enviar um número de telefone ativo para alinharmos a entrega?

Aguardo o retorno!

Atenciosamente,
{colaborador}""",

    "Endereço Não Localizado":
"""Olá, prezado cliente! Tudo bem? Esperamos que sim!

A transportadora {transportadora} tentou realizar a entrega de sua mercadoria, porém, não localizou o endereço.

Para solicitarmos uma nova tentativa de entrega à transportadora, poderia por gentileza, nos confirmar dados abaixo:

Rua:
Número:
Bairro:
CEP:
Cidade:
Estado:
Ponto de Referência:
Recebedor:
Telefone:

Após a confirmação dos dados acima, iremos solicitar que a transportadora realize uma nova tentativa de entrega que irá ocorrer no prazo de até 3 a 5 dias úteis. Caso não tenhamos retorno, o produto será devolvido ao nosso Centro de Distribuição e seguiremos com o cancelamento da compra.

Atenciosamente,
{colaborador}""",

    "Área de Risco":
"""Olá, prezado cliente! Tudo bem? Espero que sim!

A transportadora {transportadora}, informou que está com dificuldades para realizar a entrega no endereço cadastrado no portal. Dessa forma, peço por gentileza que nos informe um endereço alternativo e também telefones ativos para melhor comunicação.

Caso não possua um outro endereço, sua mercadoria ficará disponível para retirada da base da transportadora.

Qualquer dúvida me coloco à disposição para ajudá-lo!

Atenciosamente,
{colaborador}""",

    "Extravio / Avaria":
"""Olá, prezado cliente! Tudo bem? Espero que sim!

Infelizmente fomos informados pela transportadora {transportadora} que sua mercadoria foi furtada/avariada em transporte. Antes de tudo, pedimos desculpas pelo ocorrido e por todo transtorno causado.

Gostaríamos de saber se o senhor aceita o envio de uma nova mercadoria? O prazo para entrega é de 5 a 7 dias úteis, podendo ocorrer antes.

Novamente, pedimos desculpas. Qualquer dúvida me coloco à disposição para ajudá-lo!

Atenciosamente,
{colaborador}""",

    "Recusa de Entrega":
"""Prezado cliente,

A transportadora {transportadora} informou que a entrega foi recusada. Houve algum problema com a apresentação da carga? O senhor deseja o cancelamento da compra?

Caso não tenhamos retorno e o produto seja devolvido ao nosso estoque, seguiremos com o cancelamento da compra.

Qualquer dúvida me coloco à disposição para ajudá-lo!

Atenciosamente,
{colaborador}""",

    "Solicitação de Barramento":
"""Olá, prezado cliente! Tudo bem? Esperamos que sim!

Solicitamos à transportadora {transportadora} que barre a entrega da sua mercadoria. Caso tentem realizar a entrega, gentileza recusar o recebimento.

Assim que a mercadoria der entrada em nosso estoque, liberamos o estorno.

Atenciosamente,
{colaborador}""",

    "Garantia de A a Z (Amazon)":
"""Olá, prezado cliente! Tudo bem? Esperamos que sim!

Diante da abertura da Garantia A a Z, solicitamos à transportadora {transportadora} responsável que barre a entrega e aguardaremos a confirmação da suspensão da entrega, a fim de possibilitar a liberação do reembolso pela plataforma.

Atenciosamente,
{colaborador}""",

    "Em caso de Reembolso":
"""Olá, prezado cliente! Tudo bem? Esperamos que sim!

O cancelamento foi liberado conforme solicitado. O reembolso é realizado de acordo com a forma de pagamento da compra:

Para pagamentos com boleto, o reembolso será feito na conta bancária especificada pelo cliente ou como um vale-presente. Se todos os dados da sua conta bancária estiverem corretos, o reembolso pode levar até 3 dias úteis para constar na conta.

Caso você tenha pago com cartão de crédito, dependendo da data de fechamento e vencimento do seu cartão, o reembolso pode levar de uma a duas faturas.

Para pagamento em PIX, o reembolso será realizado na conta PIX em um dia útil.

Atenciosamente,
{colaborador}""",

    "Mercadoria sem Estoque":
"""Olá, prezado cliente! Tudo bem? Esperamos que sim!

Houve um erro no sistema que vendeu um item a mais e o lojista não possui a mercadoria disponível em estoque no momento. Verificamos com o nosso fornecedor, e infelizmente não tem a previsão de entrega de um novo lote.

Pedimos desculpas pelo transtorno causado.

Gostaríamos de saber se podemos seguir com o cancelamento do pedido para que a loja da compra possa realizar o estorno total.

Atenciosamente,
{colaborador}""",

    "Endereço em Zona Rural":
"""Olá, prezado cliente! Tudo bem? Esperamos que sim!

A transportadora {transportadora} nos informou que está com dificuldades para realizar a entrega no endereço cadastrado no portal.

Peço por gentileza que nos informe um endereço alternativo e também telefones ativos para melhor comunicação. Caso o senhor não possua um outro endereço, sua mercadoria ficará disponível para retirada a base da transportadora.

Atenciosamente,
{colaborador}""",

    "Reenvio de Produto":
"""Olá, prezado cliente! Tudo bem? Esperamos que sim!

Conforme solicitado, realizamos o envio de um novo produto ao senhor. Em até 48h você terá acesso a sua nova nota fiscal e poderá acompanhar os passos de sua entrega:

Link: https://ssw.inf.br/2/rastreamento_pf?
(Necessário inserir o CPF)

Novamente peço desculpas por todo transtorno causado.

Atenciosamente,
{colaborador}"""
}

# --- INTERFACE (LADO ESQUERDO) ---

col1, col2 = st.columns([1, 2]) # Coluna da esquerda menor, direita maior

with col1:
    st.subheader("Configuração")
    
    # Seleção de Colaborador e Transportadora
    colab_selecionado = st.selectbox("👤 Colaborador:", lista_colaboradores)
    transp_selecionada = st.selectbox("🚛 Transportadora:", lista_transportadoras)
    
    st.info("👆 Selecione os nomes acima para preencher automaticamente as variáveis da mensagem.")

# --- INTERFACE (LADO DIREITO - TEXTO) ---

with col2:
    st.subheader("Mensagem")
    
    # Seleção do Modelo
    tipo_mensagem = st.selectbox("Selecione o motivo do contato:", list(modelos.keys()))
    
    # Lógica de Substituição
    texto_cru = modelos[tipo_mensagem]
    
    # O Python substitui APENAS se encontrar a palavra chave no texto.
    # Se o texto não tiver {transportadora}, ele ignora e segue a vida.
    texto_final = texto_cru.replace("{transportadora}", transp_selecionada)
    texto_final = texto_final.replace("{colaborador}", colab_selecionado)
    
    # Exibe o texto pronto
    st.text_area("Copie o texto abaixo:", value=texto_final, height=400)
    
    # Botão auxiliar de Feedback Visual
    if st.button("Confirmar Cópia"):
        st.success("Texto pronto! Use Ctrl+C na caixa acima.")