# -*- coding: utf-8 -*-

import dash_core_components as dcc
import dash_html_components as html

import common as cmn
from histog_plot import histog_plot


def get_histog_plot(attr, date_idx, state, county):
    '''
    plot histogram of the data shown in the map
    '''
    if cmn.current_geo == cmn.geo_areas[0]:
        data = cmn.state_df.loc[cmn.dates[date_idx]]
    else:
        data = cmn.county_df.loc[cmn.dates[date_idx]]
    values = data[attr]
    return histog_plot(values, xlabel=cmn.attributes[attr]['name'])


def get_filter(attr, date_idx, state, county, enable=True):
    histog = get_histog_plot(attr, date_idx, state, county)
    nbins = histog['data'][0].nbinsx
    return html.Div(
        id='filter_'+attr,
        children=[
            dcc.Graph(
                id='filter_histog_' + attr,
                config=cmn.graph_config(),
                figure=histog
            ),
            dcc.RangeSlider(
                id='filter_slider_' + attr,
                updatemode='mouseup',
                min=0,
                max=nbins,
                step=1,
                value=[0, nbins]
            )
        ],
        style={'width': cmn.filter_wd,
               'display': 'block' if enable else 'none'
              }  
    )    


def get_filters_div(selected_filters):
    return html.Div(
        id='Filters',
        children=[
            html.H3('Filters', style={
                'textAlign': 'left',
            }),
            dcc.Dropdown(
                id='filter_attrs',
                options=[{'label': cmn.attributes[val]['name'], 'value': val} for val in cmn.attributes.keys()],
                value=selected_filters,
                searchable=False,
                multi=True,
                placeholder="Select filter attributes",
                style={'fontSize': '18px'}
            ),
        ] + [get_filter(attr, cmn.current_date_idx, None, None, attr in selected_filters) for attr in cmn.attributes.keys()],
        style={'width': cmn.filter_wd}
    )


def get_filters_div_horiz(selected_filters):
    return html.Div(
        id='Filters',
        children=[
            html.Div(
                children=[
                    html.H3('Filters', style={
                        'textAlign': 'left',
                    }),
                    dcc.Dropdown(
                        id='filter_attrs',
                        options=[{'label': cmn.attributes[val]['name'], 'value': val} for val in cmn.attributes.keys()],
                        value=selected_filters,
                        searchable=False,
                        multi=True,
                        placeholder="Select filter attributes",
                        style={'fontSize': '18px'}
                    ),
                ],
                style={'width': cmn.filter_dropdn_wd}
            )] + [get_filter(attr, cmn.current_date_idx, None, None, attr in selected_filters) for attr in cmn.attributes.keys()],
        style={'width': cmn.h_filter_wd, 'display': 'flex'},
        className='row'
    )


