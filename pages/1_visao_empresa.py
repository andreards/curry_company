#Libraries
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from haversine import haversine
import streamlit as st
import PIL.Image as imgpil #biblioteca boa para imagens
# from PIL import Image e dai la na parte que coloca a imagem usar Image.open , os dois dao certo
import folium
from streamlit_folium import folium_static

st.set_page_config(page_title='A Visão da Empresa', page_icon='📈', layout='wide')

# ------------------------------------------
# Funções
# ------------------------------------------

def country_maps( df1 ):
    cols = ['Delivery_location_longitude','Delivery_location_latitude','City','Road_traffic_density']
    data_plot =( df1.loc[:, cols]
                    .groupby(['City','Road_traffic_density'])
                    .median()
                    .reset_index() )

    map_ = folium.Map( zoom_start=11 )
    for index, location_info in data_plot.iterrows(): 
        folium.Marker( [location_info['Delivery_location_latitude'],
                        location_info['Delivery_location_longitude']],
                        popup=location_info[['City', 'Road_traffic_density']] ).add_to( map_ )

    folium_static( map_, width=1024, height=600 )
            
    return None

def order_share_by_week( df1 ):       
    df1_aux1 = df1[['ID','week_of_year']].groupby('week_of_year').count().reset_index()
    df1_aux2 = df1[['Delivery_person_ID','week_of_year']].groupby('week_of_year').nunique().reset_index()
    df1_aux= pd.merge(df1_aux1, df1_aux2, how='inner')
    df1_aux['order_by_delivery'] = df1_aux['ID'] / df1_aux['Delivery_person_ID']
    fig = px.line( df1_aux, x='week_of_year', y='order_by_delivery' )
    return fig
        
def order_by_week( df1 ):
    df_aux = df1.loc[:,['ID','week_of_year']].groupby('week_of_year').count().reset_index()
    df_aux.columns =['qtd_entregas','semana']
    fig = px.line(df_aux, y='semana', x='qtd_entregas')
    return fig

def traffic_order_city( df1 ):
    df1_aux = df1.loc[:,['ID','Road_traffic_density','City']].groupby(['Road_traffic_density','City']).count().reset_index()
    fig = px.scatter(df1_aux, x='City', y='Road_traffic_density', size='ID')
    return fig

def order_metric( df1 ):
    df1_aux = df1.loc[:, ['ID', 'Order_Date']].groupby('Order_Date').count().reset_index()
    df1_aux.columns = ['order_date', 'qtde_entregas'] 
    fig = px.bar(df1_aux, x='order_date', y='qtde_entregas')
    return fig

def traffic_order_share( df1 ):
    df1_aux = df1.loc[:,['ID','Road_traffic_density']].groupby('Road_traffic_density').count().reset_index()
    df1_aux['perc_ID'] = 100*(df1_aux['ID']/df1_aux['ID'].sum())
    fig = px.pie(df1_aux, values='perc_ID', names='Road_traffic_density' )
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
st.header( 'Marketplace - Visão Clientes' )

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
st.sidebar.markdown( '### Powered by Comunidade DS' )

# Filtro de Data
linhas_selecionadas = df1[ 'Order_Date' ] < date_slider
df1 = df1.loc[linhas_selecionadas, :]

# Filtro de trânsito
linhas_selecionadas = df1[ 'Road_traffic_density' ].isin( traffic_options )
df1 = df1.loc[linhas_selecionadas, :]


# =============================================
# Layout no Streamlit
# =============================================

tab1, tab2, tab3 = st.tabs( ['Visão Gerencial', 'Visão Tática', 'Visão Geográfica'] )

with tab1:
    with st.container():
        fig = order_metric( df1 )
        st.header( 'Orders by Day' )
        st.plotly_chart( fig, use_container_width=True )
        
         
    with st.container():
        col1, col2 = st.columns( 2 )
        
        with col1:
            fig=traffic_order_share( df1 )
            st.header( 'Traffic Order Share' )
            st.plotly_chart( fig, use_container_width=True )
                 
        with col2:
            fig=traffic_order_city( df1 )
            st.header( 'Traffic Order City' )
            st.plotly_chart( fig, use_container_width=True )
            
            
with tab2: # aqui o Meigarom criou um container para cada gráfico assim como ele fez na tab1, mas não mudou em nada o resultado, assim como pra mim também tinha dado certo a primeira parte sem o container, de qualquer forma ficam aqui os 2 jeitos de fazer e numa situação futura tem explicado.
    with st.container():
        st.header( 'Order by Week' )
        fig=order_by_week( df1 )
        st.plotly_chart( fig, use_container_width=True )
        
        
    with st.container():
        st.header( 'Order Share by Week' )
        fig = order_share_by_week( df1 )
        st.plotly_chart( fig, use_container_width=True )
        
        

with tab3:
    st.header( 'Country Maps' )
    country_maps( df1 )
    
    



