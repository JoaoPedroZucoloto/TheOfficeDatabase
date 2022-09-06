import streamlit as st
import pandas as pd
import plotly.express as px 
import random

def parte_1():
    
    # Apresentação
    st.write("""
    ## 1 - Qual o nome mais falado durante a série?
    """)
    
    # Carregando video
    try:
        video_file = open('data/output_data/qual_nome_mais_falado.mp4', 'rb')
        video_bytes = video_file.read()
        # mostrando video
        st.video(video_bytes)
    except:
        st.write('ERROR - Video não gerado')
    
    st.write('- - -')

    
def parte_2():

    # lendo excel
    data_2 = pd.read_excel('data/output_data/palavra_qtd.xlsx')
    j_p = False  # Jim and Pam
    # Apresentação
    st.write("""
    ## 2 - Quantas vezes personagem "X" falou o nome de personagem "Y"?
    """)
    
    # lista dos personagens principais
    personagens_principais = ['Michael', 'Dwight', 'Jim', 'Pam', 'Ryan', 'Andy',
                                'Stanley', 'Phyllis', 'Creed', 'Meredith', 'Darryl',
                                'Angela', 'Oscar', 'Kevin',
                                'Toby', 'Kelly', 'Erin']
    
    # SelectBox---------------------------------
    quem_falou = st.selectbox(
        'Quem falou',
        tuple(personagens_principais))
    
    random.shuffle(personagens_principais) if personagens_principais[0] == 'Michael' else 0
    
    nome_falado = st.selectbox(
        'Nome falado',
        tuple(personagens_principais)) # [::-1]
    #-------------------------------------------
    
    # Filtrando...
    pergunta_2 = data_2[
        (
            (data_2['quem_falou']==quem_falou) &
            (data_2['nome_falado']==nome_falado)
        ) |
        (
            (data_2['quem_falou']==nome_falado) &
            (data_2['nome_falado']==quem_falou)
        )]

    # Caso o nome SEJA O MESMO, apresentamos uma coisa
    if quem_falou == nome_falado:
        st.write("""
        🤔
        > Você escolheu o mesmo nome, mas mesmo assim, interessante ver quantas vezes um personagem falou o proprio nome...
        """)

        # criando bloco que vai ser reutilizado pra caramba
        block = data_2[data_2['falando_proprio_nome']==1][['quem_falou', 'nome_falado', 'qtd']] \
            .sort_values(by='qtd', ascending=False) \
                .rename(columns={'quem_falou': 'Quem Falou',
                                'nome_falado': 'Nome mencionado',
                                'qtd':'Nº de vezes'})

        # Estrutura para tabela
        hide_table_row_index = """
            <style>
            thead tr th:first-child {display:none}
            tbody th {display:none}
            </style>
            """
        st.markdown(hide_table_row_index, unsafe_allow_html=True)
        st.table(block.rename(columns={'Quem Falou': 'Disse o proprio nome'})[['Disse o proprio nome', 'Nº de vezes']]
                 .sample(3))
        
        # Titulo do gráfico
        st.write(f'####   - Quantidade de vezes em que um personagem mencionou o proprio nome')
        fig=px.bar(block, x='Quem Falou',y='Nº de vezes', color='Quem Falou', labels={
            'Quem Falou': 'Falou o proprio nome'
        })
        # Mostra grafico
        st.write(fig)
    
    # Caso contratio, algo diferente...
    else:
        cores = ['#2A3C5F', '#727980']
        cores_j_p = ['#765898']
        
        if quem_falou in ['Pam', 'Jim'] and nome_falado in ['Pam', 'Jim']:
            j_p = True
            
        if not j_p:
            st.write(f'####   - Quantidade de vezes em que *{quem_falou}* mencionou *{nome_falado}* e vice versa')
        else:
            st.write(f'Esse é muito bonito de ver ❤️')
            st.write(f'#### - Jim e Pam se chamam praticamente a mesma quantidade de vezes durante a série ❤️')
        fig=px.bar(pergunta_2, x='qtd' ,y='quem_falou', orientation='h', labels={
                            "quem_falou": "Quem falou",
                            "qtd": "Quantidade",
                            "nome_falado": "Nome falado"
                        }, color='quem_falou'
                , hover_data=["qtd", "nome_falado"])
        fig['data'][0]['marker']['color'] = cores[0] if not j_p else cores_j_p[0]
        fig['data'][1]['marker']['color'] = cores[1] if not j_p else cores_j_p[0]
        st.write(fig)
    st.write('dica: Coloca o nome do Jim e da Pam') if not j_p else st.write()
    st.write('- - -')
    
def parte_3():
    pass