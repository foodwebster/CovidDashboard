# -*- coding: utf-8 -*-

import dash_core_components as dcc
import dash_html_components as html

import common as cmn
from county_plot import county_plot
from state_plot import state_plot


def get_county_plot_data(attr, date_idx):
    data = cmn.county_df[['fips_str', attr]]
    # get max, min before selecting desired date, so color scale is invariant
    data_max = data[attr].max()
    data_min = data[attr].min()
    data = data.loc[cmn.dates[cmn.date_idx]]
    return data, data_max, data_min


def get_county_plot(attr, date_idx, wd):
    data, data_max, data_min = get_county_plot_data(attr, date_idx)
    return county_plot(data[attr], data['fips_str'], data_max, data_min, cmn.attributes[attr]['log'], "Covid-19 Data", wd=wd)


def get_state_plot_data(attr, date_idx):
    data = cmn.state_df[['State', attr]]
    data_max = data[attr].max()
    data_min = data[attr].min()
    data = data.loc[cmn.dates[date_idx]]
    return data, data_max, data_min


def get_state_plot(attr, date_idx, wd):
    data, data_max, data_min = get_state_plot_data(attr, date_idx)
    return state_plot(data[attr], data['State'], data_max, data_min, cmn.attributes[attr]['log'], "Covid-19 Data", wd=wd)


def get_map_plot(geo, attr, date_idx, wd):
    cmn.current_attr = attr
    cmn.current_date_idx = date_idx
    cmn.current_geo = geo

    if geo == cmn.geo_areas[0]:
        fig = get_state_plot(attr, date_idx, wd)
    else:
        fig = get_county_plot(attr, date_idx, wd)
    return fig


def get_map_div():
    # build mapping between index and date display data 
    # only display one date per week, include styling info
    date_ticks = dict(zip(range(len(cmn.dates)), [{'label': str(d.date()),
                                             'style': {"transform": "translate(-45px, 7px) rotate(-45deg)"}
                                             } if d.dayofweek==1 else '' for d in cmn.dates]))
    return html.Div(
        children=[
            html.Div(
                children=[
                    dcc.Dropdown(
                        id='geo',
                        options=[{'label': val, 'value': val} for val in cmn.geo_areas],
                        value=cmn.geo_areas[0],
                        searchable=False,
                        clearable=False,
                        style={'height': '30px', 'width': '150px', 'fontSize': '20px'}
                    ),
                    dcc.Dropdown(
                        id='attribute',
                        options=[{'label': cmn.attributes[attr]['name'], 'value': attr} for attr in cmn.attributes.keys()],
                        value=next(iter(cmn.attributes.keys())),
                        searchable=False,
                        clearable=False,
                        style={'height': '30px', 'width': '200px', 'font-size': '20px'}
                    ),
                ],
                className='row',
                style={'display': 'flex'}
            ),
            dcc.Graph(
                id='Map',
                config=cmn.graph_config(),
                figure=get_map_plot(cmn.geo_areas[0], 
                                    next(iter(cmn.attributes.keys())), 
                                    len(cmn.dates) - 1, 
                                    cmn.map_wd)
            ),
            dcc.Slider(
                id='date_slider',
                updatemode='mouseup',
                min=0,
                max=len(cmn.dates) - 1,
                step=None,
                marks=date_ticks,
                value=len(cmn.dates) - 1
            )
        ],
        style={'width': cmn.map_wd}
    )


def update_map(geo, attribute, date_idx, map_wd=800):
    attr = cmn.attribute or next(iter(cmn.attributes.keys()))
    geo = geo or cmn.geo_areas[0]
    return get_map_plot(geo, attr, date_idx, map_wd)


