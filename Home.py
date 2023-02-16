import streamlit as st
from PIL import Image

st.set_page_config(
    page_title='Home',
    page_icon='🎲',
    layout='wide'
    )
   
image =Image.open( 'foto_rest.jpg' )
#image_path = '/Users/andrealmeida/opt/anaconda3/envs/FTC_Final/'
#image = Image.open( image_path + 'foto_rest.jpg' )
st.sidebar.image(image, width=300 )

st.sidebar.markdown( '# Curry Company' )
st.sidebar.markdown( '## Fastest Delivery in Town' )
st.sidebar.markdown( """---""" )

st.write( '# Curry Company Growth Dashboard' )
st.markdown(
    """
    Growth Dashboard foi construído para acompanhar as métricas de crescimento dos Entregadores e Restaurantes.
    ### Como utilizar esse Dashboard ?
    - Visão Empresa:
        - Visão Gerencial: Métricas gerais de comportamento.
        - Visão Tática: Indicadores semanais de crescimento.
        - Visão Geográfica: Insights de geolocalização.
    - Visão Entregadores:
        - Acompanhamento dos indicadores semanais de crescimento
    - Visão Restaurantes:
        - Indicadores semanais de crescimento dos restaurantes.
    ### Ask for help
        - Time de Data Science no Discord.
            - @meigarom
    """                                
)