import pandas as pd
import folium
from folium.plugins import HeatMap

def gen_heatmap(name):
    df = pd.read_csv(f'{name}.csv')

    m = folium.Map(
        location=[28.5383, -82.4319],
        zoom_start=7,
        tiles='cartodbpositron'
    )

    heat_data = [[row['Latitude'], row['Longitude'], row['DamageSeverity']] 
                for index, row in df.iterrows()]

    HeatMap(
        heat_data,
        radius=15,
        blur=10,
        max_zoom=13,
        min_opacity=0.3,
        gradient={
            0.2: 'blue',
            0.4: 'cyan',
            0.6: 'lime',
            0.8: 'yellow',
            1.0: 'red'
        }
    ).add_to(m)

    title_html = '''
    <div style="position: fixed; 
                top: 20px; left: 50%;
                transform: translateX(-50%);
                background-color: white;
                padding: 10px;
                border-radius: 5px;
                z-index: 1000;
                font-size: 16px;
                font-weight: bold;">
        Hurricane Damage Severity Heatmap
    </div>
    '''
    m.get_root().html.add_child(folium.Element(title_html))

    m.save(f'{name}.html')

gen_heatmap('irma_test_data')
gen_heatmap('predicted_data')