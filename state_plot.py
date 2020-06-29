# -*- coding: utf-8 -*-

import numpy as np

import plotly.graph_objects as go
from plotly.offline import plot

import common as cmn

def state_plot(df, x_attr, y_attr, attr_name, data_max, data_min, log_data, title, wd=1000, ht=600):
    fig = go.Figure()
    if log_data:
        min_val = df[x_attr].min()/10.0 or 1.0
        plot_data = np.log10(df[x_attr] + min_val)
        plot_max = np.log10(data_max + min_val)
        plot_min = np.log10(data_min + min_val)
        tickprefix = '10^'
    else:
        plot_data = df[x_attr]
        plot_max = data_max
        plot_min = data_min
        tickprefix = ''
    fig = go.Figure(data=go.Choropleth(
        locations=df[y_attr], # Spatial coordinates
        z=plot_data, # Data to be color-coded
        locationmode='USA-states', # set of locations match entries in `locations`
        colorscale="Viridis",
        zmin=plot_min,
        zmax=plot_max,
        customdata=plot_data,
        text=df.State + '<br>' + attr_name + ': ' + cmn.series_as_string(df[x_attr]),
        hovertemplate = '<br>%{text}<extra></extra>',
        colorbar={'tickprefix': tickprefix}
        #marker_opacity=0.5,
    ))
    fig.update_layout(
        margin={"r":0,"t":0,"l":0,"b":0},
        title_text = title,
        geo_scope='usa', # limit map scope to USA
        width=wd, height=ht
    )
    return fig


def update_state_plot(fig, df, data_max, data_min, x_attr, log_data):
    values = df[x_attr]
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


if __name__ == "__main__":
    # execute only if run as a script
    from load_data import load_data

    country_df, state_df, county_df, dates = load_data()
    attributes = ['cases', 'deaths', 'total_case_rate', 'total_death_rate']
    
    attr = attributes[0]
    data = state_df[['State', attr]]
    data = data.loc[data.index.max()]
    fig = state_plot(data, attr, 'State', attr, data[attr].max(), data[attr].min(), True, "Covid-19 Cases")
    fig['data'][0]['selectedpoints'] = [1, 3, 5, 7, 9, 11, 13, 15, 17, 19]
    plot(fig)
