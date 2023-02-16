import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from haversine import haversine
import streamlit as st
import PIL.Image as imgpil #biblioteca boa para imagens
# from PIL import Image e dai la na parte que coloca a imagem usar Image.open , os dois dao certo
import folium
from streamlit_folium import folium_static
import numpy as np

st.set_page_config(page_title='A Visão dos Restaurantes', page_icon='🧅', layout='wide')

# ------------------------------------------
# Funções
# ------------------------------------------
def avg_std_time_on_traffic( df1 ):        
    df1_aux = (df1.loc[:, ['Time_taken(min)', 'City', 'Road_traffic_density']]
                  .groupby( ['City', 'Road_traffic_density'] )
                  .agg( { 'Time_taken(min)' : ['mean', 'std'] } ) )
    df1_aux.columns = ['avg_time','std_time']
    df1_aux = df1_aux.reset_index()
    fig = px.sunburst(df1_aux, path=['City', 'Road_traffic_density'], values='avg_time',
    color='std_time', color_continuous_scale='RdBu',
    color_continuous_midpoint=np.average(df1_aux['std_time']))
    return fig

def avg_std_time_graph(df1):            
    df1_aux = df1.loc[:, ['Time_taken(min)', 'City']].groupby( 'City' ).agg( { 'Time_taken(min)' : ['mean', 'std'] } )
    df1_aux.columns = ['avg_time','std_time']
    df1_aux = df1_aux.reset_index()
    fig = go.Figure()
    fig.add_trace( go.Bar( name='Control', x=df1_aux['City'], y=df1_aux['avg_time'], error_y=dict( type='data', array=df1_aux['std_time'] ) ) )
    fig.update_layout(barmode='group')
    return fig

def avg_std_time_delivery(df1, festival, op):
    """
    Essa função calcula o tempo médio de entrega e seu desvio padrão.
    Paramêtros:
        Input:
        - Df1 = Dataframe com os dados necessários para os cálculos
        - op = tipo de operação que será calculado
            'avg_time' = calcula o tempo médio de entrega
            'std_time' = calcula o desvio padrão das entregas
        Output:
        - Um dataframe com 2 colunas e 1 linha               
    """
    df1_aux = df1.loc[:,['Festival','Time_taken(min)']].groupby('Festival').agg( {'Time_taken(min)': ['mean', 'std']} )
    df1_aux.columns = ['avg_time', 'std_time']
    df1_aux = df1_aux.reset_index()
    linhas = df1_aux['Festival'] == 'Yes'
    df1_aux = np.round( df1_aux.loc[df1_aux['Festival'] == festival, op], 2 )
    return df1_aux
            

def distance( df1, fig ):     
    if fig == False:
        colunas = ['Restaurant_latitude', 'Restaurant_longitude','Delivery_location_latitude', 'Delivery_location_longitude']
        df1['distance'] = df1.loc[:,colunas].apply( lambda x:
                                        haversine(
                                        (x['Restaurant_latitude'], x['Restaurant_longitude']),
                                        (x['Delivery_location_latitude'], x['Delivery_location_longitude'])), axis=1)
        avg_distance = np.round( df1['distance'].mean(), 2 )
        return avg_distance
    else:
        colunas = ['Restaurant_latitude', 'Restaurant_longitude','Delivery_location_latitude', 'Delivery_location_longitude']
        df1['distance'] = df1.loc[:,colunas].apply( lambda x:
                                     haversine( (x['Restaurant_latitude'], x['Restaurant_longitude']),
                                                (x['Delivery_location_latitude'], x['Delivery_location_longitude'])), axis=1)
        avg_distance = df1.loc[:, ['City', 'distance']].groupby( 'City' ).mean().reset_index()
        fig = go.Figure( data=[ go.Pie( labels=avg_distance['City'], values=avg_distance['distance'], pull=[0, 0.05, 0])])
        return fig


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
st.header( 'Marketplace - Visão Restaurantes' )

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
    with st.container():
        st.title('Overall Metrics')
        
        col1, col2, col3, col4, col5, col6 = st.columns( 6 )
        
        with col1:
            delivery_unique = df1['Delivery_person_ID'].nunique()
            col1.metric( 'Drivers', delivery_unique )
            
        with col2:
            avg_distance = distance( df1, fig=False )
            col2.metric( 'AVG Distance', avg_distance )
                        
        with col3:
            df1_aux = avg_std_time_delivery(df1, 'Yes', 'avg_time')
            col3.metric('AVG Time w/ Festival', df1_aux)
                            
        with col4:
            df1_aux = avg_std_time_delivery(df1, 'Yes', 'std_time')
            col4.metric('STD w/ Festival', df1_aux)
            
        with col5:
            df1_aux = avg_std_time_delivery(df1, 'No', 'avg_time')
            col5.metric('AVG time w/o Festival', df1_aux)
            
        with col6:
            df1_aux = avg_std_time_delivery(df1, 'No', 'std_time')            
            col6.metric('STD w/o Festival', df1_aux)
            
    with st.container():
        st.markdown("""---""")
        st.title('Tempo Médio de Entrega por Cidade')
        col1, col2 = st.columns( 2 )
        
        with col1:
            fig = avg_std_time_graph(df1)
            st.plotly_chart( fig, use_container_width=True )
            
            
        with col2:
            
            cols = ['Time_taken(min)', 'City', 'Type_of_order']
            df1_aux = df1.loc[:, ['Time_taken(min)', 'City', 'Type_of_order']].groupby( ['City', 'Type_of_order'] ).agg( { 'Time_taken(min)' : ['mean', 'std'] } )
            df1_aux.columns = ['avg_time','std_time']
            df1_aux = df1_aux.reset_index()
            st.dataframe(df1_aux)
            
        
    with st.container():
        st.markdown("""---""")
        st.title('Distribuição do Tempo')
        col1, col2 = st.columns( 2 )
        with col1:
            fig = distance( df1, fig=True )
            st.plotly_chart( fig, use_container_width=True )
                    
        with col2:
            fig = avg_std_time_on_traffic( df1 )
            st.plotly_chart( fig, use_container_width=True )
            
            
            
