# -*- coding: utf-8 -*-

import dash_core_components as dcc
import dash_html_components as html

import common as cmn
from county_plot import county_plot
from state_plot import state_plot


def get_county_plot_data(attr, date_idx):
    data = cmn.county_df[['fips_str', attr, 'State', 'County Name']]
    # get max, min before selecting desired date, so color scale is invariant
    data_max = data[attr].max()
    data_min = data[attr].min()
    data = data.loc[cmn.dates[date_idx]]
    return data, data_max, data_min


def get_county_plot(attr, date_idx, wd, ht):
    data, data_max, data_min = get_county_plot_data(attr, date_idx)
    return county_plot(data, attr, 'fips_str', cmn.attributes[attr]['name'],
                       data_max, data_min, 
                       cmn.attributes[attr]['log'], "Covid-19 Data", 
                       wd=wd, ht=ht)


def get_state_plot_data(attr, date_idx):
    data = cmn.state_df[['State', attr]]
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


def get_map_div():
    return html.Div(
        children=[
            html.Div(
                children=[
                    dcc.Dropdown(
                        id='geo',
                        options=[{'label': val, 'value': val} for val in cmn.geo_areas],
                        value=cmn.current_geo,
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
                figure=get_map_plot(cmn.current_geo, 
                                    next(iter(cmn.attributes.keys())), 
                                    len(cmn.dates) - 1, 
                                    cmn.map_wd,
                                    cmn.map_ht)
            ),
        ],
        style={'width': cmn.map_wd, 'marginBottom': 40},
    )


def update_map(geo, attribute, date_idx):
    attr = attribute or next(iter(cmn.attributes.keys()))
    geo = geo or cmn.geo_areas[0]
    return get_map_plot(geo, attr, date_idx, cmn.map_wd, cmn.map_ht)


