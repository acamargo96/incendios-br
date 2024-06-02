import streamlit as st

import os
from datetime import datetime

import numpy as np

import pydeck as pdk

from dataprep import dataprep

os.makedirs('maps', exist_ok = True)

if 'df' in st.session_state:
    df = st.session_state['df']

else:
    df = dataprep()
    st.session_state['df'] = df

years = st.multiselect(
    'Selecione os anos',
    df['data_pas'].dt.year.unique()
)

if years:
    mask = np.zeros(df.shape[0]).astype(bool)
    for year in years:
        mask |= df['data_pas'].dt.year == int(year)

else:
    mask = np.ones(df.shape[0]).astype(bool)
    
df_summary = df[mask][['estado', 'lat_r', 'lon_r']].groupby(['lat_r', 'lon_r']).count().reset_index()

# st.header('Dados Originais')
# st.write(f'{df.shape[0]:,.0f} linhas e {df.shape[1]} colunas')
# st.dataframe(df.head())
# st.header('Dados Resumidos')
# st.write(f'{df_summary.shape[0]:,.0f} linhas e {df_summary.shape[1]} colunas')
# st.dataframe(df_summary.rename(columns = {'estado' : 'qtd'}).head())

layer = pdk.Layer(
    "HeatmapLayer",
    df_summary,
    opacity=1,
    get_position=["lon_r", "lat_r"],
    get_weight="estado",
    # pickable = True
)

view_state = pdk.ViewState(latitude=-18.51800, longitude=-55.02800, zoom=3, bearing=0, pitch=30)

deck_1 = pdk.Deck(layers=[layer], initial_view_state=view_state, tooltip={'html': 'Quantidade de Incêndios: {estado}'})

st.pydeck_chart(deck_1)

min_count = df_summary['estado'].min()
max_count = df_summary['estado'].max()
diff = max_count - min_count

color_scheme = f"""[
255 - (255-189) * (estado - {min_count})/{diff}, 
255 - 255 * (estado - {min_count})/{diff}, 
178 - (178-38) * (estado - {min_count})/{diff}
]"""

elevation_scale = st.slider(
    'Escala da Elevação das Colunas',
    min_value = 10,
    max_value = 1000,
    value = 250
)

layer = pdk.Layer(
    "ColumnLayer",
    df_summary,
    # opacity=1,
    get_position=["lon_r", "lat_r"],
    get_fill_color = color_scheme, #'[255 - estado, 255 - 0.5 * estado, 0]',
    get_elevation="estado",
    elevation_scale=elevation_scale,
    radius=10_000,
    pickable=True,
    auto_highlight=True,
)

# Set the viewport location
view_state = pdk.ViewState(latitude=-18.51800, longitude=-55.02800, zoom=3, bearing=0, pitch=30)

# Render
deck_2 = pdk.Deck(layers=[layer], initial_view_state=view_state, tooltip={'html': 'Quantidade de Incêndios: {estado}'})

st.pydeck_chart(deck_2)

def export_html():
    now = datetime.now().strftime('%Y%m%d%H%M%S')
    with st.spinner('Exportando arquivos HTML...'):
        deck_1.to_html(f'maps/heatmap_{now}.html')
        deck_2.to_html(f'maps/columnmap_{now}.html')
        
    st.success('Arquivos exportados na pasta "maps"!', icon="✅")

col_1, _, _ = st.columns([1, 1, 3])

btn_html = col_1.button('Exportar HTML', on_click = export_html)
