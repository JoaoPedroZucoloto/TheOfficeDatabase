from csv import excel
import os
import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
from wordcloud import WordCloud, STOPWORDS
from collections import Counter
import re

import bar_chart_race as bcr

class Gerador():
    
    def __init__(self):
        """ Aqui, vamos checar quais arquivos precisam ser carregador """
        
        # Caminhos dos arquivos
        self.path_arquivos = 'data/output_datar/'
        self.path_initial_data = 'data/kaggle/'
        
        # Arquivos necessários
        self.list_de_arquivos = ['qual_nome_mais_falado.mp4', 'palavra_qtd.xlsx']
        self.pasta_existe = os.path.isdir(self.path_arquivos)
        
        self.personagens_principais = ['Michael', 'Dwight', 'Jim', 'Pam', 'Ryan', 'Andy',
                                'Stanley', 'Phyllis', 'Creed', 'Meredith', 'Darryl',
                                'Angela', 'Oscar', 'Kevin',
                                'Toby', 'Kelly', 'Erin']
        
        if not self.pasta_existe:
            os.mkdir(self.path_arquivos)
            print(f'Diretório {self.path_arquivos} Sic Mvndvs Creatvs Est')
            
            self.palavra_qtd, self.eps, self.lines = self.read_data()
            
            if not self.palavra_qtd.empty:
                self.generate_video_1()
                

    def read_data(self):
        try:
            # lendo episodios e renomeando colunas
            eps = pd.read_excel(f'{self.path_initial_data}the_office_episodes.xlsx')
            eps.rename(columns={'season': 'temporada', 'episode_num_in_season': 'episodio', 'episode_num_overall': 'episodeo_num_geral', 'title': 'titulo',
                                'directed_by': 'dirigido_por', 'written_by': 'escrito_por', 'original_air_date': 'data_de_estreia', 'prod_code': 'codigo',
                                'us_viewers': 'telespectadores_USA'}, inplace=True)

            # lendo imdb e renomando colunas
            imdb = pd.read_excel(f'{self.path_initial_data}the_office_imdb.xlsx')
            imdb.rename(columns={'season': 'temporada', 'episode_num': 'episodio', 'title': 'titulo', 'original_air_date': 'data_de_estreia',
                                'imdb_rating': 'nota_imdb', 'total_votes': 'numero_de_votos', 'desc': 'descricao'}, inplace=True)

            # juntando as informações e deletando colunas
            eps = eps.merge(imdb, on='titulo', suffixes=('', '_delme'))
            eps = eps[[c for c in eps.columns if not c.endswith('_delme')]]
            eps = eps[['temporada', 'episodio', 'episodeo_num_geral', 'titulo', 'descricao', 'dirigido_por',
                       'escrito_por', 'data_de_estreia', 'codigo', 'telespectadores_USA', 'nota_imdb', 'numero_de_votos']]
            del imdb

            # lendo series e renomeado colunas
            series = pd.read_excel(f'{self.path_initial_data}the_office_series.xlsx')
            series.rename(columns={'Season': 'temporada', 'EpisodeTitle': 'titulo', 'Ratings': 'nota',
                                   'Viewership': 'audiencia', 'Duration': 'duração', 'GuestStars': 'estrelas_convidadas'}, inplace=True)

            # juntando as informações e deletando colunas
            eps = eps.merge(series, on='titulo', suffixes=('', '_delme'))
            eps = eps[[c for c in eps.columns if not c.endswith('_delme')]]
            del series

            # mudando tipo para str
            for item in ['titulo', 'descricao', 'dirigido_por', 'escrito_por', 'estrelas_convidadas']:
                eps[item] = eps[item].astype('string')

            # lendo falas e renomeando colunas
            lines = pd.read_excel(f'{self.path_initial_data}lines_official.xlsx')
            lines.rename(columns={'season': 'temporada', 'episode': 'episodio', 'title': 'titulo', 'scene': 'cena',
                                  'speaker': 'personagem', 'line_text': 'fala', 'deleted':'deletada'}, inplace=True)
            lines = lines[['id', 'temporada', 'episodio', 'cena', 'personagem', 'fala', 'deletada']]

            # limpando '[]'
            lines['fala'] = lines['fala'].str.replace(r"[\(\[].*?[\)\]]", '', regex=True)
            lines['fala'] = lines['fala'].str.replace("���", ' ', regex=True)
            lines['fala'] = lines['fala'].str.replace("��", ' ', regex=True)
            lines['fala'] = lines['fala'].str.replace("�", ' ', regex=True)
            lines['fala'] = lines['fala'].str.strip()

            # droppando falas/cenas deletadas
            lines = lines[lines['deletada'] == False]
            lines['personagem'] = lines['personagem'].astype('string')
            lines['fala'] = lines['fala'].astype('string')
            lines['fala'].replace('', np.nan, inplace=True)
            lines.dropna(subset=['fala'], inplace=True)
            lines['n_palavras'] = [len(x.split()) for x in lines['fala'].tolist()]

            # Adicionando mais informações para cada episodio
            temporada = lines['temporada'].unique().tolist()
            ref = {
                'temporada':[],
                'episodio':[],
                'qtd_cena':[],
                'nº de falas':[],
                'nº de palavras':[],
                'nº de personagens dis':[],
                'quem_iniciou_eps':[],
                'quem_finalizou_eps':[],
                'lista_personagens':[]
            }

            for t in temporada:
                    filt = lines[lines['temporada']==t]
                    episodeos = filt['episodio'].unique().tolist()
                    
                    for e in episodeos:
                        ult = filt[filt['episodio']==e]
                        personagens = ult['personagem'].unique().tolist()

                        for p in personagens:
                            if '|' in p:
                                for i in p.split('|'):
                                    personagens.append(i.strip())

                        personagens = [ x for x in personagens if "|" not in x ]
                        personagens = [j.strip() for j in personagens]
                        personagens = list(dict.fromkeys(personagens))
                        
                        ref['temporada'].append(t)
                        ref['episodio'].append(e)
                        ref['qtd_cena'].append(ult['cena'].max())
                        ref['nº de falas'].append(ult['fala'].count())
                        ref['nº de palavras'].append(ult['n_palavras'].sum())
                        ref['nº de personagens dis'].append(len(ult['personagem'].unique().tolist()))
                        ref['lista_personagens'].append(str(personagens)[1:-1])
                        ref['quem_iniciou_eps'].append(personagens[0])
                        ref['quem_finalizou_eps'].append(personagens[-1])

            plus_data = pd.DataFrame(ref)

            eps = eps.merge(plus_data, on=['temporada', 'episodio'], suffixes=('', '_delme'))
            eps = eps[[c for c in eps.columns if not c.endswith('_delme')]]
            eps = eps.drop(columns=['id', 'Unnamed: 2', 'About'])

            ref = {
                'quem_falou':[],
                'nome_falado':[],
                'qtd':[],
                'falando_proprio_nome':[]
            }

            def quem_falou_quem(quem_falou, nome_falado):
                all_falas = []

                cut = lines[lines['personagem']==quem_falou]
                if cut.shape[0] <= 0:
                    raise Exception('Nome não consta na base de dados')
                cut_l = cut['fala'].tolist()
                for f in cut_l:
                    fala = re.sub('[^a-zA-Z]+', ' ', f).strip()
                    for f_ in fala.split(' '):
                        all_falas.append(f_.lower())

                counter = Counter(all_falas)
                palavras_qtd = pd.DataFrame(counter, index=[0])
                palavras_qtd = pd.melt(palavras_qtd, value_vars=palavras_qtd.columns.tolist())
                palavras_qtd.rename(columns={'variable': 'palavra', 'value': 'qtd'}, inplace=True)
                try:
                    q_x_falou = palavras_qtd[palavras_qtd['palavra']==nome_falado.lower()]['qtd'].values[0]
                except:
                    q_x_falou = 0

                return quem_falou, nome_falado, q_x_falou

            for quem_falou in self.personagens_principais:
                for nome_falado in self.personagens_principais:
                    q_f, n_f, q_x_f = quem_falou_quem(quem_falou=quem_falou, nome_falado=nome_falado)
                    ref['quem_falou'].append(q_f)
                    ref['nome_falado'].append(n_f)
                    ref['qtd'].append(q_x_f)
                    ref['falando_proprio_nome'].append(1 if quem_falou == nome_falado else 0)
            palavra_qtd = pd.DataFrame(ref)

            # ordem
            eps = eps[['temporada', 'episodio', 'episodeo_num_geral', 'titulo', 'descricao', 'dirigido_por',
                    'escrito_por', 'data_de_estreia', 'Date', 'estrelas_convidadas', 'codigo', 'telespectadores_USA',
                    'nota_imdb', 'nota', 'audiencia', 'duração', 'qtd_cena', 'nº de falas', 'quem_iniciou_eps',
                    'quem_finalizou_eps', 'nº de palavras', 'nº de personagens dis', 'lista_personagens']]

            eps = eps.rename(columns={
                'Date':'data_formatada',
                'nº de falas': 'n_falas',
                'nº de palavras':'n_palavras',
                'nº de personagens dis':'n_personagens_distintos'
            })

            palavra_qtd.to_excel(f'{self.path_arquivos}palavra_qtd.xlsx', index=False)
            eps.to_excel(f'{self.path_arquivos}eps.xlsx', index=False)
            lines.to_excel(f'{self.path_arquivos}lines.xlsx', index=False)

            return palavra_qtd, eps, lines
        except Exception as e:
            print(e)
            return False

    def generate_video_1(self):

        ref = {
            'tempisodio':[],
            'nome':[],
            'qtd':[]
        }

        for pp in self.personagens_principais:
            for t in self.eps['temporada'].unique().tolist():
                filtrado = self.lines[self.lines['temporada']==t]
                for e in filtrado['episodio'].unique().tolist():
                    filtrado_e = filtrado[filtrado['episodio']==e]
                    qtd = filtrado_e['fala'].str.contains(pp).sum()
                    ref['tempisodio'].append('Temporada ' + str(t) + ' Episódio ' + str(e))
                    ref['nome'].append(pp)
                    ref['qtd'].append(qtd)

        r_1 = pd.DataFrame(ref)
        r_1 = pd.pivot_table(r_1, values='qtd', index='tempisodio', columns='nome')

        for pp in self.personagens_principais:
            r_1[pp] = r_1[pp].cumsum()

        title = 'Qual o nome mais mencionado na série?'
        bcr.bar_chart_race(df=r_1, filename=f'{self.path_arquivos}qual_nome_mais_falado.mp4', orientation='h', sort='desc',
                            fixed_order=False, fixed_max=True, title=title, steps_per_period=60, period_length=250
        )
        print(f'Video - {title} Sic Mvndvs Creatvs Est')
