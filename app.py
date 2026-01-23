import streamlit as st
import os

# Configuração da página
st.set_page_config(page_title="Sistema Integrado", page_icon="🏢", layout="wide")

# ==========================================
#           MENU LATERAL (COM LOGO)
# ==========================================
st.sidebar.title("Navegação")

# --- TENTA MOSTRAR A LOGO ---
# Certifique-se de que o nome do arquivo aqui seja IGUAL ao que você subiu no GitHub
# Pode ser "logo.png", "logo.jpg", "imagem.jpeg", etc.
nome_do_arquivo_logo = "logo.png" 

if os.path.exists(nome_do_arquivo_logo):
    st.sidebar.image(nome_do_arquivo_logo, use_container_width=True)
else:
    # Se não achar a imagem, não faz nada (não trava o site)
    pass

st.sidebar.markdown("Selecione o departamento:")

pagina_escolhida = st.sidebar.radio(
    "Ir para:",
    ("Pendências Logísticas", "SAC / Atendimento")
)
st.sidebar.markdown("---")
st.sidebar.caption("Sistema Interno - Engage Eletro")

# ==========================================
#      DADOS DO SETOR DE PENDÊNCIAS
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


# ==========================================
#          DADOS DO SETOR DE SAC
# ==========================================

colaboradores_sac = sorted([
    "Ana Carolina", "Ana Victoria", "Dolores", "Cassia", 
    "Juliana", "Tamara", "Rafaela", "Mylena", 
    "Isadora", "Lorrayne", "Leticia"
])

modelos_sac = {
    "Solicitação de Coleta": 
"""Olá,

Vimos que você se encontra dentro do prazo de troca / cancelamento e neste caso iremos solicitar ao setor responsável para que seja gerada a nota fiscal de coleta e seja encaminhada para a transportadora responsável para a realização do recolhimento da mercadoria.

Instruções de devolução:
- Favor devolver as mercadorias em suas embalagens originais ou similares.
- A transportadora irá realizar a coleta das mercadorias em sua residência nos próximos 15/20 dias úteis. Favor enviar dentro da embalagem um xerox da Nota Fiscal.

Ressaltamos que após a coleta do seu produto, estaremos prosseguindo com as tratativas do seu atendimento de acordo com o solicitado.

Equipe de atendimento Engage Eletro.
{colaborador}""",

    "Barrar Entrega na Transportadora":
"""Olá,

Iremos solicitar a transportadora responsável que barre a entrega. Caso tentem realizar a entrega, gentileza recusar o recebimento.
Assim que o produto retornar à Engage Eletro seguiremos com as tratativas conforme políticas de troca ou reembolso.

Equipe de atendimento Engage Eletro.
{colaborador}""",

    "Assistência Técnica (Dentro dos 7 dias)":
"""Olá,

O processo de troca tem um prazo de até 20 dias úteis a contar da data da solicitação de coleta, realizada por nós lojistas.
Como forma de solucionar o seu problema de forma rápida, gentileza acionar a assistência técnica da ................ segue abaixo informações:
................................................................

Caso seja inviável a assistência técnica, gentileza nos informar assim verificaremos a possibilidade de troca mediante disponibilidade do nosso estoque.

Equipe de atendimento Engage Eletro.
{colaborador}""",

    "Prazos de Reembolso":
"""Olá!

A devolução do valor ocorrerá na mesma forma de pagamento escolhida no momento da compra:
- Para pagamentos com boleto, o reembolso será feito na conta bancária especificada pelo cliente ou como um vale-presente. Se todos os dados da sua conta bancária estiverem corretos, o reembolso pode levar até 3 dias úteis para constar na conta.
- Caso você tenha pago com cartão de crédito, dependendo da data de fechamento e vencimento do seu cartão, o reembolso pode levar de uma a duas faturas.
- Para pagamento em PIX, o reembolso será realizado na conta PIX em um dia útil.

Equipe de atendimento Engage Eletro.
{colaborador}""",

    "Assistência Técnica (Fora dos 7 dias)":
"""Olá,

Verificamos que a sua compra foi realizada no dia ................. pela respectiva NF-...............
Sendo assim, se encontra fora do prazo para solicitar cancelamento/troca, porém está amparada pela garantia e assistência autorizada da fabricante em casos de defeito de funcionamento do produto.

Segue o link para a localização de um posto autorizado mais próximo à sua residência:
............................................

Equipe de atendimento Engage Eletro.
{colaborador}""",

    "Troca de Modelo (Dentro de 7 dias)":
"""Olá,

A troca é realizada em caso de divergência de pedido, defeito ou avaria. Não efetuamos troca por modelo, cor, voltagem.
Neste caso você deseja ficar com o produto recebido ou deseja com o reembolso da compra?

Equipe de atendimento Engage Eletro.
{colaborador}""",

    "Código Postal":
"""Olá,

Segue abaixo o código de para logística reversa do produto. Para utilizá-lo deverá ir até uma agência dos correios com o produto devidamente embalado levando consigo, obrigatoriamente, o Código de Autorização.

......................................................
(OBS1: O processo de logística reversa não gera custo algum para o cliente. Não é necessário cadastrar remetente ou destinatário, pois o código já possui todos os dados necessários).

Após devolução e o produto retornar ao nosso Centro de Distribuição, seguiremos com as tratativas conforme o solicitado.

Equipe de atendimento Engage Eletro.
{colaborador}""",

    "Reenvio Solicitado":
"""Olá,

O seu novo envio foi solicitado, em até 72h úteis o pedido será liberado.

Equipe de atendimento Engage Eletro.
{colaborador}""",

    "Acareação":
"""Olá,

Iremos solicitar junto a transportadora responsável a acareação de sua entrega, onde a mesma irá até o local de entrega verificar o recebedor.
O prazo para realização das tratativas e de 7 dias úteis.

Equipe de atendimento Engage Eletro.
{colaborador}""",

    "Confirmação de Entrega":
"""Olá,

Conforme o rastreio da transportadora ..............., o produto foi entregue no dia .......................
Segue o comprovante de entrega. (QUANDO ESTIVER DISPONÍVEL E ASSINADO)

Caso você desconheça o recebimento da mercadoria, gentileza nos informar que seguiremos com uma acareação do recebimento e iniciaremos as buscas pela mercadoria.

Equipe de atendimento Engage Eletro.
{colaborador}""",

    "Conversão GLP/GNV":
"""Olá,

Sua mercadoria sai de fábrica ajustado para GLP (gás de botijão) a conversão do gás natural (GNV) conforme manual de instruções.
Quando a conversão é realizada pela própria assistência autorizada da fabricante, o produto continua amparado pela garantia da mesma.

Fabricante: ..............
Site: ...........................

Equipe de atendimento Engage Eletro.
{colaborador}""",

    "Solicitação de Dados Bancários":
"""Olá,

Gentileza informar os dados abaixo para que reembolso seja feito:

Nome do titular da compra:
CPF do titular da compra:
Nome do banco:
Chave Pix:

Equipe de atendimento Engage Eletro.
{colaborador}""",

    "Oferecer Desconto por Avaria":
"""Olá,
Lamentamos pelo ocorrido,

Temos duas opções neste caso, mas primeiramente gostaríamos de saber se o produto está funcionando normalmente.
Caso esteja funcionando e julgar pertinente conseguimos fazer um reembolso no valor de R$ ............. reais pela permanência do produto e seguirá amparando (a) pela assistência da fabricante.

Se aceitar peço que nos informe os dados abaixo:
Nome do titular da compra:
CPF do titular da compra:
Nome do banco:
Chave Pix:

Equipe de atendimento Engage Eletro.
{colaborador}""",

    "Insucesso na Entrega (Solicitar dados)":
"""Olá,

A transportadora nos informou está com dificuldades para finalizar a entrega. Peço por gentileza que confirme os dados abaixo e telefones ativos.

Rua:
Cep:
Número:
Bairro:
Cidade:
Estado:
Complemento:
Ponto de Referência:
2 telefones ativos:

Caso não tenhamos retorno, o produto será devolvido ao nosso estoque e seguiremos com o reembolso da compra.

Equipe de atendimento Engage Eletro.
{colaborador}""",

    "Nova Tentativa de Entrega":
"""Olá,

Encaminhamos as informações para a transportadora que seguirá com uma nova tentativa de entrega que irá ocorrer no prazo de 5 a 7 dias úteis, podendo ocorrer antes.

Equipe de atendimento Engage Eletro.
{colaborador}""",

    "Mercadoria em Trânsito":
"""Olá,

De acordo com o rastreio seu pedido já consta em trânsito, com previsão de ser finalizada até o dia............................., podendo ocorrer antes.
Segue abaixo o link de rastreio:

Link: .................................
Nota fiscal: ................
Transportadora: ..........................
Para rastrear basta utilizar o CPF do titular da compra.

Equipe de atendimento Engage Eletro.
{colaborador}""",

    "Erro de Integração":
"""Olá,

Pedimos desculpas pelo transtorno. Tivemos um erro de integração em alguns pedidos, mas não se preocupe que a equipe de TI já está resolvendo e em breve será liberado.
Agradecemos a sua compreensão e, mais uma vez, pedimos desculpas pelo inconveniente causado.

Equipe de atendimento Engage Eletro.
{colaborador}""",

    "Erro de Integração com Atraso":
"""Olá,
Pedimos desculpas pela demora,

Tivemos um erro de integração em alguns pedidos, que acarretou em atrasos em toda operação de envio dos pedidos.
Solicitamos prioridade nos pedidos em atraso, para que seja liberados o mais rápido possível.

Agradecemos a sua compreensão e, mais uma vez, pedimos desculpas pelo inconveniente causado.

Equipe de atendimento Engage Eletro.
{colaborador}""",

    "Extravio Aguardar Confirmação":
"""Olá,

Gostaríamos de informar que a transportadora identificou uma possível situação de extravio no seu pedido. Estamos trabalhando com empenho junto à transportadora para localizá-lo o mais rápido possível.

Pedimos a gentileza de aguardar um prazo de 48 horas para que possamos confirmar essa situação e dar um retorno definitivo.
Caso o pedido não seja localizado dentro deste prazo, iniciaremos os procedimentos necessários para garantir sua satisfação.

Equipe de atendimento Engage Eletro.
{colaborador}""",

    "Extravio com Opção de Reenvio":
"""Olá,
Pedimos desculpas por qualquer transtorno causado,

Conforme verificamos junto a transportadora, ocorreu o extravio de sua mercadoria durante o envio do item.
Logo gostaríamos de saber como deseja seguir com a compra: Reenvio ou reembolso da mesma?

Agradecemos a sua compreensão e, mais uma vez, pedimos desculpas pelo inconveniente causado.

Equipe de atendimento Engage Eletro.
{colaborador}""",

    "Fiscalização":
"""Olá,

Verificamos que seu pedido está parado na fiscalização, mas não se preocupe já estamos em contato com a transportadora ............................. para agilizar a liberação.
Contudo, sua mercadoria sofrerá atrasos na entrega, mas não se preocupe, assim que a mercadoria for liberada, iremos solicitar máxima prioridade em sua entrega.

Equipe de atendimento Engage Eletro.
{colaborador}""",

    "Item Faltante":
"""Olá,

Iremos solicitar ao nosso estoque que verifique se temos o item para envio separadamente.

Equipe de atendimento Engage Eletro.
{colaborador}""",

    "Atraso na Entrega":
"""Olá,

Lamentamos pelo atraso ocorrido na entrega do seu pedido.
Estamos em contato com a transportadora para verificar o ocorrido, solicitamos a previsão de entrega e prioridade para que seja finalizado o mais rápido possível.

Equipe de atendimento Engage Eletro.
{colaborador}""",

    "Entrega (Serviços não inclusos)":
"""Olá,

O transporte realizado pela Engage Eletro junto as transportadoras parceiras, abrange somente a entrega do produto na entrada (porta, portaria) do local indicado por você no momento da compra, não incluindo outros serviços como, montagem ou desmontagem de produtos, subida de escadas, transporte por guincho, instalação, entre outros.

Reforçamos que as entregas ocorrem de segunda à sexta em horário comercial.

Equipe de atendimento Engage Eletro.
{colaborador}""",

    "Agradecimento":
"""Olá,

Que bom, fico feliz que tenha dado tudo certo.
Se você tiver alguma dúvida, preocupação ou sugestão, não hesite em entrar em contato conosco.
Estamos aqui para ajudá-la da melhor maneira possível.

Equipe de atendimento Engage Eletro.
{colaborador}""",

    "Código Coleta Domiciliar":
"""Olá,

Segue abaixo o código para logística reversa do produto. Para utilizá-lo o produto deve está devidamente embalado no dia da coleta.

......................................................
(OBS1: O processo de logística reversa não gera custo algum para o cliente. Não é necessário cadastrar remetente ou destinatário, pois o código já possui todos os dados necessários).

Após devolução e o produto retornar ao nosso Centro de Distribuição, seguiremos com as tratativas conforme o solicitado.

Equipe de atendimento Engage Eletro.
{colaborador}""",

    "Embalagem Similar":
"""Olá,

Informamos que, para garantir a integridade do produto durante o processo de devolução, recomendamos o uso de embalagens adequadas, como o envolvimento do produto em plástico bolha ou a utilização de camadas de papelão. Estas medidas ajudam a evitar danos adicionais ao item e asseguram uma devolução segura.

Agradecemos pela compreensão e estamos à disposição para qualquer dúvida.

Equipe de atendimento Engage Eletro.
{colaborador}""",

    "Termo para Troca Casada":
"""Olá,

Para verificarmos a possibilidade de prosseguimento com à entrega do produto no momento da coleta, propomos a formalização por meio de um Termo de Acordo Extrajudicial que será encaminhado pelo nosso jurídico.

O procedimento funciona da seguinte forma:
- Encaminharemos o termo, que deverá ser assinado em todas as páginas, conforme o documento de identificação apresentado (RG, CNH, etc.);
- O termo assinado, juntamente com a foto do documento de identificação, deve ser enviado de volta em até 48 horas;
- Após o recebimento, nosso departamento jurídico fará a validação;
- Com a validação concluída, daremos sequência às tratativas de envio e coleta dos produtos.

Podemos seguir com esse procedimento?

Equipe de atendimento Engage Eletro.
{colaborador}""",

    "Recusa de Troca (Avaria)":
"""Conforme já informado anteriormente, é necessário realizar a troca do produto avariado, a fim de evitar problemas futuros fora do prazo de atendimento pela loja.

Diante da sua recusa em efetuar a troca, entendemos que o(a) senhor(a) está ciente e assumindo o risco de permanecer com um produto que apresenta avaria física, abrindo mão de qualquer reivindicação posterior relacionada a esse dano, e isentando a loja de toda e qualquer responsabilidade futura quanto a esse aspecto.

Ressaltamos que o produto permanece coberto pela garantia do fabricante exclusivamente para defeitos de funcionamento, conforme previsto em garantia legal e contratual. Avarias físicas não são cobertas por essa garantia.

Permanecemos à disposição para qualquer esclarecimento adicional.

Equipe de atendimento Engage Eletro.
{colaborador}""",

    "Rastreio Indisponível (Jadlog)":
"""Gostaríamos de esclarecer que seu pedido foi despachado regularmente e dentro do prazo previsto pela modalidade de entrega escolhida.
Contudo, o sistema de rastreamento da transportadora está temporariamente indisponível, o que nos impede de fornecer informações atualizadas sobre a localização do pedido neste momento.

Já notificamos a transportadora parceira responsável e estamos acompanhando de perto para que o sistema seja restabelecido o quanto antes.

Agradecemos a compreensão e pedimos desculpas pelo transtorno causado.
Atenciosamente,

Equipe de atendimento Engage Eletro.
{colaborador}"""
}


# ==========================================
#           LÓGICA DAS PÁGINAS
# ==========================================

def pagina_pendencias():
    st.header("🚚 Setor de Pendências / Logística")
    st.markdown("---")
    
    col1, col2 = st.columns([1, 2])
    with col1:
        st.info("Configuração")
        # Rótulo padronizado para "Colaborador"
        colab = st.selectbox("👤 Colaborador:", colaboradores_pendencias, key="colab_p")
        transp = st.selectbox("🚛 Transportadora:", lista_transportadoras, key="transp_p")

    with col2:
        opcao = st.selectbox("Motivo:", list(modelos_pendencias.keys()), key="msg_p")
        texto_cru = modelos_pendencias[opcao]
        
        texto_final = texto_cru.replace("{transportadora}", transp)
        texto_final = texto_final.replace("{colaborador}", colab)
        
        st.text_area("Texto Final:", value=texto_final, height=500)
        if st.button("Confirmar (Pendências)", key="btn_p"):
            st.success("Copiado!")

def pagina_sac():
    st.header("🎧 Setor de SAC / Atendimento")
    st.markdown("---")
    
    col1, col2 = st.columns([1, 2])
    with col1:
        st.info("Configuração SAC")
        # AQUI NÃO TEM MAIS TRANSPORTADORA, SOMENTE COLABORADOR
        colab = st.selectbox("👤 Colaborador:", colaboradores_sac, key="colab_s")

    with col2:
        opcao = st.selectbox("Motivo:", list(modelos_sac.keys()), key="msg_s")
        texto_cru = modelos_sac[opcao]
        
        # Apenas substitui o colaborador
        texto_final = texto_cru.replace("{colaborador}", colab)
        
        st.text_area("Texto Final:", value=texto_final, height=500)
        st.caption("Nota: Se houver pontilhados (....) no texto, preencha manualmente após copiar.")
        
        if st.button("Confirmar (SAC)", key="btn_s"):
            st.success("Copiado!")

# ==========================================
#           ROTEAMENTO (PÁGINA ESCOLHIDA)
# ==========================================

if pagina_escolhida == "Pendências Logísticas":
    pagina_pendencias()
else:
    pagina_sac()
