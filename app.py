import streamlit as st
import os

# Configuração da página
st.set_page_config(page_title="Sistema Integrado", page_icon="🚀", layout="wide")

# ==========================================
#      DESIGN BLINDADO (CSS ANTI-BUG)
# ==========================================
# Este CSS garante que o visual fique perfeito mesmo em computadores com Modo Escuro
st.markdown("""
<style>
    /* 1. IMPORTANDO FONTE MODERNA */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    /* 2. FORÇAR CORES (Mesmo se o PC estiver em modo escuro) */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        color: #1e293b !important; /* Força texto cinza escuro */
        background-color: #f1f5f9 !important; /* Força fundo claro */
    }

    /* 3. BARRA LATERAL */
    section[data-testid="stSidebar"] {
        background-color: #0f172a !important; /* Fundo escuro */
    }
    /* Texto da barra lateral sempre branco */
    section[data-testid="stSidebar"] * {
        color: #f8fafc !important;
    }

    /* 4. TÍTULOS */
    h1, h2, h3 {
        color: #1e40af !important; /* Azul Royal */
    }

    /* 5. CAIXAS DE SELEÇÃO E TEXTO */
    .stSelectbox div[data-baseweb="select"] > div, 
    .stTextArea textarea {
        background-color: #ffffff !important;
        color: #000000 !important; /* Texto preto forçado */
        border: 1px solid #cbd5e1;
        border-radius: 12px;
    }
    
    /* Garante que o texto dentro do dropdown seja legível */
    ul[data-baseweb="menu"] li {
        background-color: #ffffff !important;
        color: #000000 !important;
    }

    /* 6. CAIXA DE CÓPIA (A CORREÇÃO PRINCIPAL) */
    /* Isso arruma o bug de "letra branca no fundo branco" */
    .stCodeBlock {
        background-color: #ffffff !important;
        border: 1px solid #cbd5e1;
        border-radius: 12px;
    }
    .stCodeBlock pre {
        background-color: #ffffff !important;
    }
    .stCodeBlock code {
        color: #000000 !important; /* Texto do código preto */
        font-family: 'Inter', sans-serif !important;
        white-space: pre-wrap !important; /* Quebra linha se for muito longo */
    }
    /* Remove cores estranhas de sintaxe do Streamlit */
    .stCodeBlock span {
        color: #000000 !important;
    }

    /* 7. BOTÕES */
    .stButton button {
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%) !important;
        color: white !important;
        border: none;
        padding: 0.8rem 2rem;
        border-radius: 12px;
        font-weight: 600;
        width: 100%;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 10px rgba(0,0,0,0.2);
    }
    
    /* Pequenos ajustes */
    label {
        color: #475569 !important;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
#           MENU LATERAL
# ==========================================

if os.path.exists("logo.png"):
    st.sidebar.image("logo.png", use_container_width=True)

st.sidebar.title("Navegação")
st.sidebar.markdown("Selecione o módulo:")

pagina_escolhida = st.sidebar.radio(
    "Ir para:",
    ("Pendências Logísticas", "SAC / Atendimento")
)

st.sidebar.markdown("---")
st.sidebar.markdown("""
<div style="text-align: center; color: #94a3b8; font-size: 12px;">
    Engage Eletro<br>Sistema Interno v4.0 (Dark Mode Fix)
</div>
""", unsafe_allow_html=True)

# ==========================================
#      DADOS (Listas e Dicionários)
# ==========================================

colaboradores_pendencias = sorted([
    "Ana", "Mariana", "Gabriela", "Layra", 
    "Maria Eduarda", "Akisia", "Marcelly", "Camilla"
])

lista_transportadoras = sorted([
    "4ELOS", "ATUAL", "BRASIL WEB", "FAVORITA", "FRONTLOG", 
    "GENEROSO", "JADLOG", "LOGAN", "MMA", "PAJUÇARA", 
    "PATRUS", "REBOUÇAS", "REDE SUL", "RIO EXPRESS", 
    "TJB", "TOTAL", "TRILOG"
])

colaboradores_sac = sorted([
    "Ana Carolina", "Ana Victoria", "Dolores", "Cassia", 
    "Juliana", "Tamara", "Rafaela", "Mylena", 
    "Isadora", "Lorrayne", "Leticia"
])

# Mensagens Pendências
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

# Mensagens SAC
modelos_sac = {
    "Solicitação de Coleta": """Olá,\n\nVimos que você se encontra dentro do prazo de troca / cancelamento e neste caso iremos solicitar ao setor responsável para que seja gerada a nota fiscal de coleta e seja encaminhada para a transportadora responsável para a realização do recolhimento da mercadoria.\n\nInstruções de devolução:\n- Favor devolver as mercadorias em suas embalagens originais ou similares.\n- A transportadora irá realizar a coleta das mercadorias em sua residência nos próximos 15/20 dias úteis. Favor enviar dentro da embalagem um xerox da Nota Fiscal.\n\nRessaltamos que após a coleta do seu produto, estaremos prosseguindo com as tratativas do seu atendimento de acordo com o solicitado.\n\nEquipe de atendimento Engage Eletro.\n{colaborador}""",
    "Barrar Entrega na Transportadora": """Olá,\n\nIremos solicitar a transportadora responsável que barre a entrega. Caso tentem realizar a entrega, gentileza recusar o recebimento.\nAssim que o produto retornar à Engage Eletro seguiremos com as tratativas conforme políticas de troca ou reembolso.\n\nEquipe de atendimento Engage Eletro.\n{colaborador}""",
    "Assistência Técnica (Dentro dos 7 dias)": """Olá,\n\nO processo de troca tem um prazo de até 20 dias úteis a contar da data da solicitação de coleta, realizada por nós lojistas.\nComo forma de solucionar o seu problema de forma rápida, gentileza acionar a assistência técnica da ................ segue abaixo informações:\n................................................................\n\nCaso seja inviável a assistência técnica, gentileza nos informar assim verificaremos a possibilidade de troca mediante disponibilidade do nosso estoque.\n\nEquipe de atendimento Engage Eletro.\n{colaborador}""",
    "Prazos de Reembolso": """Olá!\n\nA devolução do valor ocorrerá na mesma forma de pagamento escolhida no momento da compra:\n- Para pagamentos com boleto, o reembolso será feito na conta bancária especificada pelo cliente ou como um vale-presente. Se todos os dados da sua conta bancária estiverem corretos, o reembolso pode levar até 3 dias úteis para constar na conta.\n- Caso você tenha pago com cartão de crédito, dependendo da data de fechamento e vencimento do seu cartão, o reembolso pode levar de uma a duas faturas.\n- Para pagamento em PIX, o reembolso será realizado na conta PIX em um dia útil.\n\nEquipe de atendimento Engage Eletro.\n{colaborador}""",
    "Assistência Técnica (Fora dos 7 dias)": """Olá,\n\nVerificamos que a sua compra foi realizada no dia ................. pela respectiva NF-...............\nSendo assim, se encontra fora do prazo para solicitar cancelamento/troca, porém está amparada pela garantia e assistência autorizada da fabricante em casos de defeito de funcionamento do produto.\n\nSegue o link para a localização de um posto autorizado mais próximo à sua residência:\n............................................\n\nEquipe de atendimento Engage Eletro.\n{colaborador}""",
    "Troca de Modelo (Dentro de 7 dias)": """Olá,\n\nA troca é realizada em caso de divergência de pedido, defeito ou avaria. Não efetuamos troca por modelo, cor, voltagem.\nNeste caso você deseja ficar com o produto recebido ou deseja com o reembolso da compra?\n\nEquipe de atendimento Engage Eletro.\n{colaborador}""",
    "Código Postal": """Olá,\n\nSegue abaixo o código de para logística reversa do produto. Para utilizá-lo deverá ir até uma agência dos correios com o produto devidamente embalado levando consigo, obrigatoriamente, o Código de Autorização.\n\n......................................................\n(OBS1: O processo de logística reversa não gera custo algum para o cliente. Não é necessário cadastrar remetente ou destinatário, pois o código já possui todos os dados necessários).\n\nApós devolução e o produto retornar ao nosso Centro de Distribuição, seguiremos com as tratativas conforme o solicitado.\n\nEquipe de atendimento Engage Eletro.\n{colaborador}""",
    "Reenvio Solicitado": """Olá,\n\nO seu novo envio foi solicitado, em até 72h úteis o pedido será liberado.\n\nEquipe de atendimento Engage Eletro.\n{colaborador}""",
    "Acareação": """Olá,\n\nIremos solicitar junto a transportadora responsável a acareação de sua entrega, onde a mesma irá até o local de entrega verificar o recebedor.\nO prazo para realização das tratativas e de 7 dias úteis.\n\nEquipe de atendimento Engage Eletro.\n{colaborador}""",
    "Confirmação de Entrega": """Olá,\n\nConforme o rastreio da transportadora ..............., o produto foi entregue no dia .......................\nSegue o comprovante de entrega. (QUANDO ESTIVER DISPONÍVEL E ASSINADO)\n\nCaso você desconheça o recebimento da mercadoria, gentileza nos informar que seguiremos com uma acareação do recebimento e iniciaremos as buscas pela mercadoria.\n\nEquipe de atendimento Engage Eletro.\n{colaborador}""",
    "Conversão GLP/GNV": """Olá,\n\nSua mercadoria sai de fábrica ajustado para GLP (gás de botijão) a conversão do gás natural (GNV) conforme manual de instruções.\nQuando a conversão é realizada pela própria assistência autorizada da fabricante, o produto continua amparado pela garantia da mesma.\n\nFabricante: ..............\nSite: ...........................\n\nEquipe de atendimento Engage Eletro.\n{colaborador}""",
    "Solicitação de Dados Bancários": """Olá,\n\nGentileza informar os dados abaixo para que reembolso seja feito:\n\nNome do titular da compra:\nCPF do titular da compra:\nNome do banco:\nChave Pix:\n\nEquipe de atendimento Engage Eletro.\n{colaborador}""",
    "Oferecer Desconto por Avaria": """Olá,\nLamentamos pelo ocorrido,\n\nTemos duas opções neste caso, mas primeiramente gostaríamos de saber se o produto está funcionando normalmente.\nCaso esteja funcionando e julgar pertinente conseguimos fazer um reembolso no valor de R$ ............. reais pela permanência do produto e seguirá amparando (a) pela assistência da fabricante.\n\nSe aceitar peço que nos informe os dados abaixo:\nNome do titular da compra:\nCPF do titular da compra:\nNome do banco:\nChave Pix:\n\nEquipe de atendimento Engage Eletro.\n{colaborador}""",
    "Insucesso na Entrega (Solicitar dados)": """Olá,\n\nA transportadora nos informou está com dificuldades para finalizar a entrega. Peço por gentileza que confirme os dados abaixo e telefones ativos.\n\nRua:\nCep:\nNúmero:\nBairro:\nCidade:\nEstado:\nComplemento:\nPonto de Referência:\n2 telefones ativos:\n\nCaso não tenhamos retorno, o produto será devolvido ao nosso estoque e seguiremos com o reembolso da compra.\n\nEquipe de atendimento Engage Eletro.\n{colaborador}""",
    "Nova Tentativa de Entrega": """Olá,\n\nEncaminhamos as informações para a transportadora que seguirá com uma nova tentativa de entrega que irá ocorrer no prazo de 5 a 7 dias úteis, podendo ocorrer antes.\n\nEquipe de atendimento Engage Eletro.\n{colaborador}""",
    "Mercadoria em Trânsito": """Olá,\n\nDe acordo com o rastreio seu pedido já consta em trânsito, com previsão de ser finalizada até o dia............................., podendo ocorrer antes.\nSegue abaixo o link de rastreio:\n\nLink: .................................\nNota fiscal: ................\nTransportadora: ..........................\nPara rastrear basta utilizar o CPF do titular da compra.\n\nEquipe de atendimento Engage Eletro.\n{colaborador}""",
    "Erro de Integração": """Olá,\n\nPedimos desculpas pelo transtorno. Tivemos um erro de integração em alguns pedidos, mas não se preocupe que a equipe de TI já está resolvendo e em breve será liberado.\nAgradecemos a sua compreensão e, mais uma vez, pedimos desculpas pelo inconveniente causado.\n\nEquipe de atendimento Engage Eletro.\n{colaborador}""",
    "Erro de Integração com Atraso": """Olá,\nPedimos desculpas pela demora,\n\nTivemos um erro de integração em alguns pedidos, que acarretou em atrasos em toda operação de envio dos pedidos.\nSolicitamos prioridade nos pedidos em atraso, para que seja liberados o mais rápido possível.\n\nAgradecemos a sua compreensão e, mais uma vez, pedimos desculpas pelo inconveniente causado.\n\nEquipe de atendimento Engage Eletro.\n{colaborador}""",
    "Extravio Aguardar Confirmação": """Olá,\n\nGostaríamos de informar que a transportadora identificou uma possível situação de extravio no seu pedido. Estamos trabalhando com empenho junto à transportadora para localizá-lo o mais rápido possível.\n\nPedimos a gentileza de aguardar um prazo de 48 horas para que possamos confirmar essa situação e dar um retorno definitivo.\nCaso o pedido não seja localizado dentro deste prazo, iniciaremos os procedimentos necessários para garantir sua satisfação.\n\nEquipe de atendimento Engage Eletro.\n{colaborador}""",
    "Extravio com Opção de Reenvio": """Olá,\nPedimos desculpas por qualquer transtorno causado,\n\nConforme verificamos junto a transportadora, ocorreu o extravio de sua mercadoria durante o envio do item.\nLogo gostaríamos de saber como deseja seguir com a compra: Reenvio ou reembolso da mesma?\n\nAgradecemos a sua compreensão e, mais uma vez, pedimos desculpas pelo inconveniente causado.\n\nEquipe de atendimento Engage Eletro.\n{colaborador}""",
    "Fiscalização": """Olá,\n\nVerificamos que seu pedido está parado na fiscalização, mas não se preocupe já estamos em contato com a transportadora ............................. para agilizar a liberação.\nContudo, sua mercadoria sofrerá atrasos na entrega, mas não se preocupe, assim que a mercadoria for liberada, iremos solicitar máxima prioridade em sua entrega.\n\nEquipe de atendimento Engage Eletro.\n{colaborador}""",
    "Item Faltante": """Olá,\n\nIremos solicitar ao nosso estoque que verifique se temos o item para envio separadamente.\n\nEquipe de atendimento Engage Eletro.\n{colaborador}""",
    "Atraso na Entrega": """Olá,\n\nLamentamos pelo atraso ocorrido na entrega do seu pedido.\nEstamos em contato com a transportadora para verificar o ocorrido, solicitamos a previsão de entrega e prioridade para que seja finalizado o mais rápido possível.\n\nEquipe de atendimento Engage Eletro.\n{colaborador}""",
    "Entrega (Serviços não inclusos)": """Olá,\n\nO transporte realizado pela Engage Eletro junto as transportadoras parceiras, abrange somente a entrega do produto na entrada (porta, portaria) do local indicado por você no momento da compra, não incluindo outros serviços como, montagem ou desmontagem de produtos, subida de escadas, transporte por guincho, instalação, entre outros.\n\nReforçamos que as entregas ocorrem de segunda à sexta em horário comercial.\n\nEquipe de atendimento Engage Eletro.\n{colaborador}""",
    "Agradecimento": """Olá,\n\nQue bom, fico feliz que tenha dado tudo certo.\nSe você tiver alguma dúvida, preocupação ou sugestão, não hesite em entrar em contato conosco.\nEstamos aqui para ajudá-la da melhor maneira possível.\n\nEquipe de atendimento Engage Eletro.\n{colaborador}""",
    "Código Coleta Domiciliar": """Olá,\n\nSegue abaixo o código para logística reversa do produto. Para utilizá-lo o produto deve está devidamente embalado no dia da coleta.\n\n......................................................\n(OBS1: O processo de logística reversa não gera custo algum para o cliente. Não é necessário cadastrar remetente ou destinatário, pois o código já possui todos os dados necessários).\n\nApós devolução e o produto retornar ao nosso Centro de Distribuição, seguiremos com as tratativas conforme o solicitado.\n\nEquipe de atendimento Engage Eletro.\n{colaborador}""",
    "Embalagem Similar": """Olá,\n\nInformamos que, para garantir a integridade do produto durante o processo de devolução, recomendamos o uso de embalagens adequadas, como o envolvimento do produto em plástico bolha ou a utilização de camadas de papelão. Estas medidas ajudam a evitar danos adicionais ao item e asseguram uma devolução segura.\n\nAgradecemos pela compreensão e estamos à disposição para qualquer dúvida.\n\nEquipe de atendimento Engage Eletro.\n{colaborador}""",
    "Termo para Troca Casada": """Olá,\n\nPara verificarmos a possibilidade de prosseguimento com à entrega do produto no momento da coleta, propomos a formalização por meio de um Termo de Acordo Extrajudicial que será encaminhado pelo nosso jurídico.\n\nO procedimento funciona da seguinte forma:\n- Encaminharemos o termo, que deverá ser assinado em todas as páginas, conforme o documento de identificação apresentado (RG, CNH, etc.);\n- O termo assinado, juntamente com a foto do documento de identificação, deve ser enviado de volta em até 48 horas;\n- Após o recebimento, nosso departamento jurídico fará a validação;\n- Com a validação concluída, daremos sequência às tratativas de envio e coleta dos produtos.\n\nPodemos seguir com esse procedimento?\n\nEquipe de atendimento Engage Eletro.\n{colaborador}""",
    "Recusa de Troca (Avaria)": """Conforme já informado anteriormente, é necessário realizar a troca do produto avariado, a fim de evitar problemas futuros fora do prazo de atendimento pela loja.\n\nDiante da sua recusa em efetuar a troca, entendemos que o(a) senhor(a) está ciente e assumindo o risco de permanecer com um produto que apresenta avaria física, abrindo mão de qualquer reivindicação posterior relacionada a esse dano, e isentando a loja de toda e qualquer responsabilidade futura quanto a esse aspecto.\n\nRessaltamos que o produto permanece coberto pela garantia do fabricante exclusivamente para defeitos de funcionamento, conforme previsto em garantia legal e contratual. Avarias físicas não são cobertas por essa garantia.\n\nPermanecemos à disposição para qualquer esclarecimento adicional.\n\nEquipe de atendimento Engage Eletro.\n{colaborador}""",
    "Rastreio Indisponível (Jadlog)": """Gostaríamos de esclarecer que seu pedido foi despachado regularmente e dentro do prazo previsto pela modalidade de entrega escolhida.\nContudo, o sistema de rastreamento da transportadora está temporariamente indisponível, o que nos impede de fornecer informações atualizadas sobre a localização do pedido neste momento.\n\nJá notificamos a transportadora parceira responsável e estamos acompanhando de perto para que o sistema seja restabelecido o quanto antes.\n\nAgradecemos a compreensão e pedimos desculpas pelo transtorno causado.\nAtenciosamente,\n\nEquipe de atendimento Engage Eletro.\n{colaborador}"""
}

# ==========================================
#           LÓGICA DAS PÁGINAS
# ==========================================

def pagina_pendencias():
    st.title("🚚 Pendências Logísticas")
    st.markdown("Use este painel para gerar mensagens sobre tentativas de entrega, atrasos e extravios.")
    st.markdown("---")
    
    col1, col2 = st.columns([1, 2], gap="large")
    
    with col1:
        st.subheader("1. Configuração")
        colab = st.selectbox("👤 Quem é você?", colaboradores_pendencias, key="colab_p")
        transp = st.selectbox("🚛 Qual a transportadora?", lista_transportadoras, key="transp_p")

    with col2:
        st.subheader("2. Mensagem")
        opcao = st.selectbox("Qual o motivo do contato?", list(modelos_pendencias.keys()), key="msg_p")
        
        texto_cru = modelos_pendencias[opcao]
        texto_final = texto_cru.replace("{transportadora}", transp).replace("{colaborador}", colab)
        
        # MENSAGEM SUCESSO E BOTÃO DE COPIAR INTEGRADO
        st.success("Mensagem gerada! Clique no ícone de copiar 📋 que aparece no canto da caixa ao passar o mouse.")
        st.code(texto_final, language="text")

def pagina_sac():
    st.title("🎧 SAC / Atendimento")
    st.markdown("Use este painel para gerar respostas rápidas para o cliente.")
    st.markdown("---")
    
    col1, col2 = st.columns([1, 2], gap="large")
    
    with col1:
        st.subheader("1. Configuração")
        colab = st.selectbox("👤 Quem é você?", colaboradores_sac, key="colab_s")

    with col2:
        st.subheader("2. Mensagem")
        opcao = st.selectbox("Qual o motivo do contato?", list(modelos_sac.keys()), key="msg_s")
        
        texto_cru = modelos_sac[opcao]
        texto_final = texto_cru.replace("{colaborador}", colab)
        
        # MENSAGEM SUCESSO E BOTÃO DE COPIAR INTEGRADO
        st.success("Mensagem gerada! Clique no ícone de copiar 📋 que aparece no canto da caixa ao passar o mouse.")
        st.code(texto_final, language="text")
        
        st.caption("Nota: Campos pontilhados (....) devem ser preenchidos manualmente.")

# ==========================================
#           ROTEAMENTO
# ==========================================

if pagina_escolhida == "Pendências Logísticas":
    pagina_pendencias()
else:
    pagina_sac()
