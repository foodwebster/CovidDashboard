# -*- coding: utf-8 -*-

import dash_core_components as dcc
import dash_html_components as html

import common as cmn
from county_plot import county_plot, update_county_plot
from state_plot import state_plot, update_state_plot


def get_init_attr():
    return list(iter(cmn.attributes.keys()))[cmn.init_attr]
    #return list(cmn.attributes.keys())[-1]
    

def get_county_plot_data(attr, date_idx):
    attrs = ['fips_str', attr, 'State', 'County Name']
    if attr != 'population':
        attrs += ['population']
    data = cmn.county_df[attrs]
    # get max, min before selecting desired date, so color scale is invariant
    data_max = data[attr].max()
    data_min = data[attr].min()
    data = data.loc[cmn.dates[date_idx]]
    return data, data_max, data_min


def get_county_plot(attr, date_idx, wd, ht):
    data, data_max, data_min = get_county_plot_data(attr, date_idx)
    return county_plot(data, attr, 'fips_str', 
                       data_max, data_min, 
                       cmn.attributes[attr]['log'], "Covid-19 Data", 
                       wd=wd, ht=ht)


def get_state_plot_data(attr, date_idx):
    attrs = [attr, 'State']
    if attr != 'population':
        attrs += ['population']
    data = cmn.state_df[attrs]
    data_max = data[attr].max()
    data_min = data[attr].min()
    data = data.loc[cmn.dates[date_idx]]
    return data, data_max, data_min


def get_state_plot(attr, date_idx, wd, ht):
    data, data_max, data_min = get_state_plot_data(attr, date_idx)
    return state_plot(data, attr, 'State', cmn.attributes[attr]['name'],
                      data_max, data_min, 
                      cmn.attributes[attr]['log'], "Covid-19 Data", 
                      wd=wd, ht=ht)

def get_map_plot(geo, attr, date_idx, wd, ht):
    cmn.current_attr = attr
    cmn.current_date_idx = date_idx
    cmn.current_geo = geo

    if geo == cmn.geo_areas[0]:
        fig = get_state_plot(attr, date_idx, wd, ht)
    else:
        fig = get_county_plot(attr, date_idx, wd, ht)
    return fig


def update_map_figure(fig, geo, attr, date_idx):
    '''
    update map data after change in displayed attribute or date
    '''
    if geo == cmn.geo_areas[0]:
        df, data_max, data_min = get_state_plot_data(attr, date_idx)
        update_state_plot(fig, df, data_max, data_min, attr, cmn.attributes[attr]['log'])
    else:
        df, data_max, data_min = get_county_plot_data(attr, date_idx)
        update_county_plot(fig, df, data_max, data_min, attr, cmn.attributes[attr]['log'])


def get_map_div(geo):
    return html.Div(
        children=[
            html.Div(
                children=[
                    dcc.Dropdown(
                        id='geo',
                        options=[{'label': val, 'value': val} for val in cmn.geo_areas],
                        value=geo,
                        searchable=False,
                        clearable=False,
                        style={'height': '38px', 'width': '150px', 'fontSize': '15px'}
                    ),
                    cmn.attribute_selector('attribute'),
                ],
                className='row',
                style={'display': 'flex'}
            ),
            dcc.Graph(
                id='Map',
                config=cmn.graph_config(),
                figure=get_map_plot(geo, 
                                    get_init_attr(), 
                                    len(cmn.dates) - 1, 
                                    cmn.map_wd,
                                    cmn.map_ht)
            ),
        ],
        style={'width': cmn.map_wd, 'marginBottom': 40},
    )


def update_map(geo, attribute, date_idx):
    '''
    update map to new geo
    '''
    attr = attribute or get_init_attr()
    #geo = geo or cmn.geo_areas[0]
    return get_map_plot(geo, attr, date_idx, cmn.map_wd, cmn.map_ht)


