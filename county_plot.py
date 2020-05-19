# -*- coding: utf-8 -*-

from urllib.request import urlopen
import json
import numpy as np

import plotly.graph_objects as go
from plotly.offline import plot

with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
    counties = json.load(response)

def county_plot(data, locs, data_max, data_min, log_data, title, wd=1000, ht=600):
    
    fig = go.Figure()
    if log_data:
        min_val = data.min()/10.0 or 1.0
        plot_data = np.log10(data + min_val)
        plot_max = np.log10(data_max + min_val)
        plot_min = np.log10(data_min + min_val)
    else:
        plot_data = data
        plot_max = data_max
        plot_min = data_min
    fig.add_trace(
        go.Choroplethmapbox(z=plot_data, geojson=counties, locations=locs,
                           colorscale="Viridis",
                           zmin=plot_min,
                           zmax=plot_max,
                           marker_opacity=1.0,
                           visible=True, 
                           text=data
                          )        
    ) 
    fig.update_layout(mapbox_style='white-bg', # "carto-positron",
                      mapbox_zoom=3, mapbox_center = {"lat": 37.0902, "lon": -95.7129},
                      width=wd, height=ht,
                      title_text=title,
                      margin={"r":0,"t":0,"l":0,"b":0})
    '''
    fig.add_trace(
        go.Choropleth(z=log_data, geojson=counties, locations=locs,
                           colorscale="Viridis",
                           zmin=log_min,
                           zmax=log_max,
                           #marker_opacity=0.5,
                           visible=True, 
                           text=data
                          )        
    ) 
    fig.update_layout(geo_scope='usa', # limit map scope to USA
                      width=wd, height=ht,
                      margin={"r":0,"t":0,"l":0,"b":0},
                      title_text = title,
                      )
    '''
    return fig


if __name__ == "__main__":
    # execute only if run as a script
    from prepare_case_data import get_case_data
    from prepare_movement_data import get_movement_data

    country_case_df, state_case_df, county_case_df = get_case_data()
    country_mmt_df, state_mmt_df, county_mmt_df = get_movement_data()
    attributes = ['cases', 'deaths', 'total_case_rate', 'total_death_rate']
    
    attr = attributes[0]
    data = county_case_df[['fips_str', attr]]
    data = data.loc[data.index.max()]
    fig = county_plot(data[attr], data['fips_str'], data[attr].max(), data[attr].min(), True, "Covid-19 Cases")
    plot(fig)
