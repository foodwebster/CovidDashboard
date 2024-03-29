# -*- coding: utf-8 -*-

#from urllib.request import urlopen
import json
import numpy as np

import plotly.graph_objects as go
from plotly.offline import plot

import common as cmn

with open(cmn.datapath/'geojson_counties_fips.json') as response:
    counties = json.load(response)

def get_hover_text(df, values, attr_name):
    return (df['State'] + ' ' + df['County Name'] + '<br>' 
                                     + attr_name + ': ' + cmn.series_as_string(values) + '<br>'
                                     + 'Population' + ': ' + cmn.series_as_string(df['population']))

def county_plot(df, x_attr, y_attr, data_max, data_min, log_data, title, wd=1000, ht=600):
    attr_name = cmn.attributes[x_attr]['name']
    fig = go.Figure()
    values = df[x_attr]
    if log_data:
        min_val = values.min()/10.0 or 1.0
        plot_data = np.log10(values + min_val)
        plot_max = np.log10(data_max + min_val)
        plot_min = np.log10(data_min + min_val)
        tickprefix = '10^'
    else:
        plot_data = values
        plot_max = data_max
        plot_min = data_min
        tickprefix = ''
    fig.add_trace(
        go.Choroplethmapbox(z=plot_data, geojson=counties, locations=df[y_attr],
                           colorscale="Viridis",
                           zmin=plot_min,
                           zmax=plot_max,
                           marker_opacity=1.0,
                           visible=True, 
                           text=get_hover_text(df, values, attr_name),
                           hovertemplate = '<br>%{text}<extra></extra>',
                           colorbar={'tickprefix': tickprefix}
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


def update_county_plot(fig, df, data_max, data_min, x_attr, log_data):
    not_null = ~df[x_attr].isnull().to_numpy()
    values = df.loc[not_null, x_attr]
    if log_data:
        min_val = values.min()/10.0 or 1.0
        plot_data = np.log10(values + min_val)
        plot_max = np.log10(data_max + min_val)
        plot_min = np.log10(data_min + min_val)
    else:
        plot_data = values
        plot_max = data_max
        plot_min = data_min
    fig['data'][0].z = plot_data
    fig['data'][0].zmax = plot_max
    fig['data'][0].zmin = plot_min
    fig['data'][0].text = get_hover_text(df, values, cmn.attributes[x_attr]['name'])
    
    
if __name__ == "__main__":
    # execute only if run as a script
    from load_data import load_data

    country_df, state_df, county_df, dates = load_data()
    attributes = ['cases', 'deaths', 'total_case_rate', 'total_death_rate']
    
    attr = attributes[0]
    #data = county_df[['fips_str', attr]]
    data = county_df.loc[county_df.index.max()]
    fig = county_plot(data, attr, 'fips_str', data[attr].max(), data[attr].min(), True, "Covid-19 Cases")
    plot(fig)
