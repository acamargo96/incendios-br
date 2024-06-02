import os
from tqdm import tqdm
import pydeck as pdk
import pandas as pd
from pydeck.types import String

from dataprep import dataprep

os.makedirs('maps', exist_ok = True)

df = dataprep()

for year in tqdm(range(2003, 2024, 1)):

    mask = df['data_pas'].dt.year == int(year)
    df_summary = df[mask][['estado', 'lat_r', 'lon_r']].groupby(['lat_r', 'lon_r']).count().reset_index()

    txt_layer = pdk.Layer(
        "TextLayer",
        pd.DataFrame(data = {'name' : str(year), 'coordinates' : [(-18.51800, 0)]}),
        pickable=True,
        get_position="coordinates",
        get_text="name",
        get_size=25,
        get_color=[255, 255, 255],
        get_angle=0,
        # Note that string constants in pydeck are explicitly passed as strings
        # This distinguishes them from columns in a data set
        get_text_anchor=String("middle"),
        get_alignment_baseline=String("center"),
    )

    layer = pdk.Layer(
        "HeatmapLayer",
        df_summary,
        opacity=1,
        get_position=["lon_r", "lat_r"],
        get_weight="estado",
        # pickable = True
    )

    view_state = pdk.ViewState(latitude=-18.51800, longitude=-55.02800, zoom=3, bearing=0, pitch=30)

    deck_1 = pdk.Deck(layers=[txt_layer, layer], initial_view_state=view_state, tooltip={'html': 'Quantidade de Incêndios: {estado}'})

    min_count = df_summary['estado'].min()
    max_count = df_summary['estado'].max()
    diff = max_count - min_count

    color_scheme = f"""[
    255 - (255-189) * (estado - {min_count})/{diff}, 
    255 - 255 * (estado - {min_count})/{diff}, 
    178 - (178-38) * (estado - {min_count})/{diff}
    ]"""

    layer = pdk.Layer(
        "ColumnLayer",
        df_summary,
        # opacity=1,
        get_position=["lon_r", "lat_r"],
        get_fill_color = color_scheme, #'[255 - estado, 255 - 0.5 * estado, 0]',
        get_elevation="estado",
        elevation_scale=800,
        radius=10_000,
        pickable=True,
        auto_highlight=True,
    )
    
    

    # Set the viewport location
    view_state = pdk.ViewState(latitude=-18.51800, longitude=-55.02800, zoom=3, bearing=0, pitch=30)

    # Render
    deck_2 = pdk.Deck(layers=[txt_layer, layer], initial_view_state=view_state, tooltip={'html': 'Quantidade de Incêndios: {estado}'})

   
    deck_1.to_html(f'maps/heatmap_{year}.html')
    deck_2.to_html(f'maps/columnmap_{year}.html')
