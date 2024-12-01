import os
from supabase import create_client # type: ignore
from dotenv import load_dotenv
import json

from fasthtml.common import *

#load environment varibles
load_dotenv()

#initialize supabase client
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

app,rt = fast_app(
    hdrs=(
        Link(rel='stylesheet', href='https://cdn.jsdelivr.net/npm/@picocss/pico@2/css/pico.jade.min.css'),
        Html(data_theme='light'),
        Link(rel='icon', type='image/x-icon', href='logo.png'),
        Style(
            """
                :root {
                    --pico-color: #105A37 !important;
                    --pico-h1-color: #105A37 !important;
                    --pico-h2-color: #105A37 !important;
                    --pico-h3-color: #105A37 !important;
                    --pico-h4-color: #105A37 !important;
                    --pico-h5-color: #105A37 !important;
                    --pico-h6-color: #105A37 !important;
                    --pico-mark-color: #105A37 !important;
                }
            """
        )
        )
    )

def header():
    header = Nav(
        Ul(
            Li(A(Img(src='logo2.png', width='400px', height='500px', alt='EasyStocks - Logo'), href='/'))
        ),
        Ul(
            Li(A('Como Funciona', href='/funciona', cls='contrast')),
            Li(A('Sobre', href='/sobre', cls='contrast')),
            Li(Button('Escolha sua Ação', onclick="window.location.href='/escolha'"))
        ), style='padding-left: 50px; padding-right: 50px; '
    ), Style (
        """
            A:hover {
                background-color: #F9FBF2;
                border-radius: 50px;
            }
        """
    )
    return header

def footer():
    footer = Div( 
        Footer(
            H2('EasyStocks'),
            P('Made by Eduarda Lima © 2024'),
            H2(A('Pitch', href='https://www.canva.com/design/DAGVcXxy888/ZvazyEuqUb8MqEAoxO16yA/view?utm_content=DAGVcXxy888&utm_campaign=designshare&utm_medium=link&utm_source=editor', target='_blank'), style='margin-top: 0')
        ), Style (
            '''
            footer {
                display: flex; 
                justify-content: space-between;
                align-items: center; 
            }
            .footer-div {
                background-color:#F9FBF2;
                padding: 35px 50px 15px 50px;
            }
            '''
        ), cls='footer-div'
    )
    return footer

#Pagina Principal

@rt('/')
def get():
    
    page = Titled("EasyStocks", style="display: none;"), Div(
        header(),
        Div(
            H1('Slogan', style="margin-bottom: 65px;"),
            P('Não precisa ser um expert para tomar decisões informadas em seus investimentos.', cls='purpose'),
            P('Compare ações de diferentes empresas com dados em tempo real.', cls='purpose'),
            Button('Escolha Sua Ação', onclick="window.location.href='/escolha'", style="margin-top: 50px;"),
            cls='message'
        ), Style (
            """
            body, html {
                height: 100%;
                margin: 0;
                padding: 0;
            }

            .wrapper {
                display: flex;
                height: 100%;
                flex-direction: column;
                -ms-flex-direction: column;
            }

            .purpose {
                font-size: 30px !important;
                margin: 0;
            }

            .message{
                display: flex;
                flex-direction: column;
                flex: 1;
                justify-content: center;
                align-items: center;
            }

            """
        ),
        footer(),
        cls='wrapper'
    )

    return page


#Pagina Escolha

def getTable(setor: str, filters):
    query = supabase.table("teste").select("*")

    if setor != 'Todos':
        query = query.eq("Setor", setor)


    if filters['bestOption'] == True:
        query = query.lte('"P/L*P/VP"', 22.5).lte('"Dív. líquida/EBITDA"', 3.5).gte('"D.Y"', 6).gte('"CAGR Lucros 5 anos"', 12).gte('"M. Líquida"', 15).gte('ROE', 10)
        #D.Y acima de 6
        #p/vp*p/l abaixo de 22,5
        #CARG minimo 12%
        #P/L menor que CARG
        #margem liquida minimo 15%
        #ROE minimo 10%
        #DIV.LIQ/EBTIDA menor que 3,5
    
    if filters['orderValue'] == True:
        query = query.order("Valor atual")
    
    if filters['orderLetter'] == True:
        query = query.order("Ticker")

    response = query.execute()
    return response

def APIObjectTODict(object):
    jsonData = object.model_dump_json()
    parsedData = json.loads(jsonData)
    dataDict = parsedData['data']

    return dataDict

def displayTable(dict):

    if (len(list(dict)) == 0):
        return H2("Nenhum dado disponível para exibir.", style="color: red !important; text-align: center;")

    headers = list(dict[0].keys())

    table = Table(
        Thead(
            Tr(
                *[Th(h) for h in headers]
            )
        ),
        Tbody(
            *[
                Tr(
                    *[
                        Td(str(row[h])) 
                            for h in headers
                        
                    ]  # Adiciona as células de cada linha
                )
                for row in dict
            ]
        ), 
        style="width: auto; heigth: 75%;",
        cls='striped'
    )
    return table

def displayFilterTable(dict):

    if (len(list(dict)) == 0):
        return H2("Nenhum dado disponível para exibir.", style="color: red !important; text-align: center;")

    headers = list(dict[0].keys())

    table = Table(
        Thead(
            Tr(
                *[Th(h) for h in headers if h != "highlight"]
            )
        ),
        Tbody(
            *[
                Tr(
                    *[
                        Td(
                            str(row[h]["value"]),
                            cls='highlighted' if row[h]["highlight"] == True else ""
                            ) for h in headers if h != "highlight"
                        
                    ]  # Adiciona as células de cada linha
                )
                for row in dict
            ]
        ), 
        style="width: auto; heigth: 75%;",
        cls='striped'
    )
    return table


def escolhaTable(setor: str, filters):
    data = getTable(setor, filters)
    object = APIObjectTODict(data)

    if (filters['highlight'] == True):
        for row in object:
            for key, value in row.items():
                print(row[key])
                row[key] = {"value": value, "highlight": False }
                if (key == "D.Y"):
                    row[key] = {"value": value, "highlight": value >= 6.0}
                if (key == "P/L*P/VP"):
                    row[key] = {"value": value, "highlight": value <= 22.5}
                if (key == "CAGR Lucros 5 anos"):
                    row[key] = {"value": value, "highlight": value >= 12.0}
                if (key == "M. líquida"):
                    row[key] = {"value": value, "highlight": value >= 15.0}
                if (key == "ROE"):
                    row[key] = {"value": value, "highlight": value >= 10.0}
                if (key == "Div. líquida/EBITDA"):
                    row[key] = {"value": value, "highlight": value <= 3.5 }
                print(row[key])
        return displayFilterTable(object)
            
    return displayTable(object)

def SelectSetores():
    seleciona = Select(
        Option('Selecione a área em que gostaria de investir...', selected='', disabled='', value='Todos'),
        Option('Banco', value='Banco'),
        Option('Energia', value='Energia'),
        Option('Saneamento', value='Saneamento'),
        Option('Telecom', value='Telecom'),
        Option('Seguro', value='Seguro'),
        Option('Papel e Celulose', value='Papel e Celulose'),
        name='setor',  # Nome do campo para envio no formulário
        aria_label='Selecione a área em que gostaria de investir...',
        required=''
    )
    return seleciona

def filters():
    filter =  Fieldset(
            Label(
                Input(type='checkbox', id='bestOption', name='bestOption'),
                'Mostre as melhores opções', htmlfor='bestOption'),
            Label(
                Input(type='checkbox', id='highlight', name='highlight'),
                "Destaque as melhores opções", htmlfor='highlight'),
            Label(
                Input(type='checkbox', id='orderValue', name='orderValue'),
                'Ordenado por Valor', htmlfor='orderValue'),
            Label(
                Input(type='checkbox', id='orderLetter', name='orderLetter'),
                "Ordem Alfabética", htmlfor='orderLetter')
        )
    return filter


def formSetor():
    form = Form(
        Div(
            Label("Selecione o setor:", style="font-size:30px; font-weight:bold; "),
            SelectSetores(),
            Label("Selecione os filtros: (Opcional)"),
            filters(),
            Button("Enviar", type="submit"),
        ),
        action="/escolha",  # Define para onde o formulário será enviado
        method="post",
    ), Style (
        """
            Form {
                width:50%
            }
        """
    )
    return form

@rt("/escolha")
def post(setor: str = Form(...),  
    bestOption: Optional[bool] = Form(False),
    highlight: Optional[bool] = Form(False),
    orderValue: Optional[bool] = Form(False),
    orderLetter: Optional[bool] = Form(False)
    ):

    filtrosAplicados = {
        "bestOption": bestOption,
        "highlight": highlight,
        "orderValue": orderValue,
        "orderLetter": orderLetter,
    }
    table = escolhaTable(setor, filtrosAplicados)
    pageEscolha = Titled("EasyStocks | Escolha", style="display: none;"), Div (
        header(),
        Div(
            formSetor(),
            Hr(),
            Div (
                H2("Resultados para o setor:", style="margin: 0 10px;"), 
                H4(setor, style="font-weight: normal; margin:0;"), 
                Button('Limpar', onclick="window.location.href='/escolha'", style="margin: 0 20px;", cls='outline'),
                cls='textDiv'),
            table,
            cls='forms'),
        Style (
            """
            body, html {
                height: 100%;
                margin: 0;
                padding: 0;
            }  

            .wrapper {
                display: flex;
                height: 100%;
                flex-direction: column;
                -ms-flex-direction: column;
            }

            .textDiv {
                display: flex;
                flex-direction: row;
                align-items: center;
                margin-top: 10px;
            }

            .forms {
                display: flex;
                flex-direction: column;
                flex: 1;
                justify-content: center;
                align-items: center;
                padding: 70px 100px 30px 100px;
            }

            .highlighted {
                background-color: #93D9B8 !important; /* Destaca as células */
            }

            """
        ),
        footer(), 
        cls='wrapper'

    )
    return pageEscolha
    
@rt('/escolha')
def get(): 
    pageEscolha = Titled("EasyStocks | Escolha", style="display: none;"), Div (
        header(),
        Div(
            formSetor(),
            cls='forms'),
        Style (
            """
            body, html {
                height: 100%;
                margin: 0;
                padding: 0;
            }

            .wrapper {
                display: flex;
                height: 100%;
                flex-direction: column;
                -ms-flex-direction: column;
            }

            .forms {
                display: flex;
                flex-direction: column;
                flex: 1;
                justify-content: center;
                align-items: center;
                padding: 70px 100px 30px 100px;
            }

            """
        ),
        footer(), 
        cls='wrapper'

    )
    return pageEscolha


#Pagina Sobre
@rt('/sobre')
def get():
    pageSobre = Titled("EasyStocks | Sobre", style="display: none;"), Div (
        header(),
        Div(
            Div(
                H2('Sobre a Plataforma', style='color: #ffffff; margin:0;'), cls='divTitle'
            ), 
            Div (
                H4('Nossa Missão'),
                P('É proporcionar uma abordagem simples e eficaz para iniciantes  no investimento dentro mercado de ações.'),
                H4('A plataforma'),
                P('Nossa plataforma permite que você compare ações de diversas empresas dentro de um setor, oferecendo dados e análises em tempo real. Com essa ferramenta, você pode identificar oportunidades de investimento e tomar decisões informadas com confiança. Inicie sua jornada no mundo dos investimentos agora mesmo!'),
                H4('Quem pode usar?'),
                P('Nossa plataforma é voltada para jovens adultos e adultos que, embora não tenham formação em finanças, desejam dar os primeiros passos no investimento em ações!'),
                H4('Somos únicos'),
                P('Somos a única plataforma dedicada a auxiliar na tomada de decisão em investimentos em ações, utilizando uma linguagem clara e livre de jargões, além de ser amigável para iniciantes.'),
                cls='divText'
            ),
            cls='sobre'), Style (
            """
            body, html {
                height: 100%;
                margin: 0;
                padding: 0;
            }

            .wrapper {
                height: 100%;
                display: flex;
                flex-direction: column;
                -ms-flex-direction: column;
            }

            .sobre {
                display: flex;
                flex:1;
                flex-direction: column;
                -ms-flex-direction: column;
                align-items: center;
                justify-content: center;
            }

            .divTitle {
                display: flex;
                background-color: var(--pico-primary);
                width: 100%;
                align-items: center;
                justify-content: center;
                padding: 35px 0;
            }

            .divText{
                width: 100%;
                padding: 35px 175px 0;
            }

            H4 {
                margin-bottom: 10px;
            }

            """
        ),
        footer(), 
        cls='wrapper'
    )
    return pageSobre

#Pagina Funciona
@rt('/funciona')
def get():
    pageSobre = Titled("EasyStocks | Como Funciona", style="display: none;"), Div (
        header(),
        Div(
            Div(
                H2('Como Funciona', style='color: #ffffff; margin:0;'), cls='divTitle'
            ), 
            Div (
                H3('Método para escolher as Ações'),
                P('É proporcionar uma abordagem simples e eficaz para iniciantes  no investimento dentro mercado de ações.'),
                Hr(),
                H3('Entendendo a Tabela'),
                P('Nossa plataforma permite que você compare ações de diversas empresas dentro de um setor, oferecendo dados e análises em tempo real. Com essa ferramenta, você pode identificar oportunidades de investimento e tomar decisões informadas com confiança. Inicie sua jornada no mundo dos investimentos agora mesmo!'),
                H4('Quem pode usar?'),
                P('Nossa plataforma é voltada para jovens adultos e adultos que, embora não tenham formação em finanças, desejam dar os primeiros passos no investimento em ações!'),
                H4('Somos únicos'),
                P('Somos a única plataforma dedicada a auxiliar na tomada de decisão em investimentos em ações, utilizando uma linguagem clara e livre de jargões, além de ser amigável para iniciantes.'),
                cls='divText'
            ),
            cls='sobre'), Style (
            """
            body, html {
                height: 100%;
                margin: 0;
                padding: 0;
            }

            .wrapper {
                height: 100%;
                display: flex;
                flex-direction: column;
                -ms-flex-direction: column;
            }

            .sobre {
                display: flex;
                flex:1;
                flex-direction: column;
                -ms-flex-direction: column;
                align-items: center;
                justify-content: center;
            }

            .divTitle {
                display: flex;
                background-color: var(--pico-primary);
                width: 100%;
                align-items: center;
                justify-content: center;
                padding: 35px 0;
            }

            .divText{
                width: 100%;
                padding: 35px 175px 0;
            }

            """
        ),
        footer(), 
        cls='wrapper'
    )
    return pageSobre


serve()