import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from haversine import haversine
import streamlit as st
import PIL.Image as imgpil 
import folium
from streamlit_folium import folium_static

st.set_page_config(page_title='A Visão da Entregadores', page_icon='🚚', layout='wide')

# ------------------------------------------
# Funções
# ------------------------------------------
def top_delivers(df1, top_asc):                            
    df2 = (df1.loc[:,['Delivery_person_ID','Time_taken(min)','City']]
                .groupby(['City','Delivery_person_ID'])
                .mean()
                .sort_values(['City','Time_taken(min)'], ascending=top_asc)
                .reset_index())
    df1_aux1 = df2.loc[df2['City'] == 'Metropolitian', :].head(10)
    df1_aux2 = df2.loc[df2['City'] == 'Urban', :].head(10)
    df1_aux3 = df2.loc[df2['City'] == 'Semi-Urban', :].head(10)
    df3 = pd.concat ([df1_aux1, df1_aux2,df1_aux3]).reset_index(drop=True)
    return df3


def clean_code( df1 ):
    """ Essa função tem a responsabilidade de limpar o dataframe
        Tipos de limpeza:
        1- Remoção dos dados NaN
        2- Mudança de tipo da coluna de dados
        3- Remoção dos espaços das variáveis de texto
        4- Formatação da coluna de datas
        5- limpeza da coluna de tempo (remoção do texto da variável numérica)
        
        input= Dataframe
        output= Dataframe
    """

    # Limpando os espacos
    df1.loc[:, 'ID'] = df1.loc[:, 'ID'].str.strip()
    df1.loc[:, 'Road_traffic_density'] = df1.loc[:, 'Road_traffic_density'].str.strip()
    df1.loc[:, 'Type_of_order'] = df1.loc[:, 'Type_of_order'].str.strip()
    df1.loc[:, 'Type_of_vehicle'] = df1.loc[:, 'Type_of_vehicle'].str.strip()
    df1.loc[:, 'City'] = df1.loc[:, 'City'].str.strip()
    df1.loc[:, 'Festival'] = df1.loc[:, 'Festival'].str.strip()

    # 1 - passando a coluna delivery_person_age para int (numero)
    condicao_linha = df1['Delivery_person_Age'] != 'NaN '
    df1 = df1.loc[condicao_linha, : ].copy()
    df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype( int )

    # 2 - passando a coluna delivery person rates para numero decimal (float)
    df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype( float )

    # 3 - passando a coluna order date para data
    df1['Order_Date'] = pd.to_datetime(df1['Order_Date'], format='%d-%m-%Y')

    # 4 - passar o multiple deliveries para numero (int)
    condicao_linha = df1['multiple_deliveries'] != 'NaN '
    df1 = df1.loc[condicao_linha, : ].copy()
    df1['multiple_deliveries'] = df1['multiple_deliveries'].astype( int )

    # 5 - limpar os NaN
    condicao_linha = df1['Road_traffic_density'] != 'NaN'
    df1 = df1.loc[condicao_linha, : ].copy()
    condicao_linha = df1['City'] != 'NaN'
    df1 = df1.loc[condicao_linha, : ].copy()
    condicao_linha = df1['Festival'] != 'NaN'
    df1 = df1.loc[condicao_linha, : ].copy()

    # 6 - Limpar a coluna do time taken
    df1['Time_taken(min)'] = df1['Time_taken(min)'].apply( lambda x: x.split( '(min)')[1])

    # 7 - Criar a coluna week_of_year
    week_of_year = df1['Order_Date'].dt.strftime( "%U" )
    df1['week_of_year'] = week_of_year

    # 8 - Passando o Time Taken para float
    df1['Time_taken(min)'] = df1['Time_taken(min)'].astype(float)
    
    return df1

# ------------------------------------------ Inicío da Estrutura Lógica do Código ------------------------------------------
# ------------------------------------------
# Import Dataset
# ------------------------------------------
df = pd.read_csv('train.csv')

# ------------------------------------------
# limpando os dados
# ------------------------------------------
df1 = clean_code(df)

# =============================================
# Barra Lateral
# =============================================
st.header( 'Marketplace - Visão Entregadores' )

#image_path = '/Users/andrealmeida/opt/anaconda3/envs/FTC_Final/foto_rest.jpg' #seria melhor usar uma imagem .png que eh mais simples e tal mas o que importa aqui eh que deu certo (poderia ter colocado so "foto_rest.jpg" que daria certo, porem deixar o caminho completo eh mais seguro
# para encontrar o caminho correto, abra outro terminal e digite pwd, que o terminal mostra o caminho certinho e dai so adicionar o /foto_rest.jpg
image = imgpil.open( 'foto_rest.jpg' )
st.sidebar.image( image, width = 300 )

st.sidebar.markdown( '# Curry Company' )
st.sidebar.markdown( '## Fastest Delivery in Town' )
st.sidebar.markdown( """---""" )

st.sidebar.markdown( '## Selecione uma data limite' )
date_slider = st.sidebar.slider(
    'Até qual valor ?',
    value=pd.datetime(2022, 4, 13),
    min_value=pd.datetime(2022, 2, 11),
    max_value=pd.datetime(2022, 4, 6),
    format='DD-MM-YYYY'
    )
#st.dataframe( df1 ) jogar o DF no streamlit e pegar a maior e menor data e inserir nos parametros acima
st.sidebar.markdown( """---""" )

traffic_options = st.sidebar.multiselect(
    'Quais as condições de trânsito',
    ['Low', 'Medium', 'High', 'Jam'],
     default=['Low','Medium'] ) #aqui eh o valor padrao que ja vai estar la, pode ser so 1, 2 ou todos

st.sidebar.markdown( """---""" )

# Adicionar as condiçoes climaticas
condicoes_clima = st.sidebar.multiselect(
    'Selecione as condições clímaticas',
    ['conditions Cloudy', 'conditions Fog', 'conditions Sandstorms', 'conditions Stormy', 'conditions Sunny', 'conditions Windy'],
    default= 'conditions Sunny' )

st.sidebar.markdown( """---""" )
st.sidebar.markdown( '### Powered by Comunidade DS' )

# Filtro de Data
linhas_selecionadas = df1[ 'Order_Date' ] < date_slider
df1 = df1.loc[linhas_selecionadas, :]

# Filtro de trânsito
linhas_selecionadas = df1[ 'Road_traffic_density' ].isin( traffic_options )
df1 = df1.loc[linhas_selecionadas, :]

# Filtro de Condição Climática
linhas_selecionadas = df1[ 'Weatherconditions' ].isin( condicoes_clima )
df1 = df1.loc[linhas_selecionadas, :]


# =============================================
# Layout no Streamlit
# =============================================

tab1, tab2, tab3 = st.tabs( ['Visão Gerencial', '_', '_'] )

with tab1:
# ------------------------------------------ Exemplo ------------------------------------------  
# Aqui como o código é bem simples não vale a pena criar uma função, pois seria trocar seis por meia dúzia porém vou deixar aqui o exemplo que o Meigarom fez.    
#    def calculate_big_number(cols, operation):
#        if operation == 'max':
#            results = df1.loc[:, cols].max()
#        elif operation == 'min':
#            results = df1.loc[:, cols].min()
#        return results
    
#        number = calculate_big_number('Delivery_person_Age', operation='max')
#        st.metric('A Maior Idade e', value= number)
# ------------------------------------------ --------------------- --------------------- ---------------------      
    
    with st.container():
        st.title( 'Overall Metrics' )
        col1, col2, col3, col4 = st.columns( 4, gap='large' )
        with col1:
            # Maior idade dos entregadores
            maior_idade = df1['Delivery_person_Age'].max()
            col1.metric( 'Maior Idade', maior_idade )
                
        with col2:
            # Menor idade dos entregadores
            menor_idade = df1['Delivery_person_Age'].min()
            col2.metric( 'Menor Idade', menor_idade )
        
        with col3:
            # Melhor condição de veículo
            melhor_veiculo = df1['Vehicle_condition'].max()
            col3.metric( 'Melhor Condição', melhor_veiculo )
            
        with col4:
            # Pior condição de veículo
            pior_veiculo = df1['Vehicle_condition'].min()
            col4.metric( 'Pior Condição', pior_veiculo )

    with st.container():
        st.markdown( """---""" )
        st.header( 'Avaliações' )
        
        col1, col2 = st.columns( 2 )
        with col1:
            # Avaliação Médias por Entregador
            st.markdown( '##### Avaliação Média por Entregador' )
            df1_aux = ( df1[['Delivery_person_Ratings','Delivery_person_ID']]
                        .groupby('Delivery_person_ID')
                        .mean()
                        .reset_index() )
            st.dataframe( df1_aux )
            
        with col2:
            # Avaliação Média por Trânsito
            st.markdown( '##### Avaliação Média por Trânsito' )
            df1_aux = ( round(df1.loc[:,['Delivery_person_Ratings','Road_traffic_density']]
                                .groupby('Road_traffic_density')
                                .agg(['mean', 'std']), 4) )
            df1_aux.columns = ['Rating_mean','Rating_std']
            df1_aux = df1_aux.reset_index()
            st.dataframe( df1_aux )
            
            # Avaliacao media por clima   
            st.markdown( '##### Avaliação Média por Clima' )
            df1_aux = ( round(df1.loc[:,['Delivery_person_Ratings','Weatherconditions']]
                                .groupby('Weatherconditions')
                                .agg(['mean', 'std']), 4) )
            df1_aux.columns = ['Rating_mean','Rating_std']
            df1_aux = df1_aux.reset_index()
            st.dataframe( df1_aux )
            
    with st.container():
        st.markdown( """---""" )
        st.header( 'Velocidade de Entrega' )
        
        col1, col2 = st.columns( 2 )
        
        with col1:
            st.markdown( '##### Top Entregadores mais rápidos' )
            df3 = top_delivers(df1, top_asc=True)
            st.dataframe( df3 )
            
        with col2:
            st.markdown( '##### Top Entregadores mais lentos' )
            df3 = top_delivers(df1, top_asc=False)
            st.dataframe( df3 )
            
            
            
        
        
        
        
        
        
        
        
        
        