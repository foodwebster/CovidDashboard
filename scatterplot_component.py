# -*- coding: utf-8 -*-

import dash_core_components as dcc
import dash_html_components as html

import common as cmn
from scatter_plot import scatter_plot

def get_scatterplot_div():
    attrs = list(cmn.attributes.keys())
    return html.Div(
        children=[
            html.Div(
                children=[
                    "X:",
                    dcc.Dropdown(
                        id='x_attribute',
                        options=[{'label': cmn.attributes[attr]['name'], 'value': attr} for attr in cmn.attributes.keys()],
                        value=next(iter(cmn.attributes.keys())),
                        searchable=False,
                        clearable=False,
                        style={'height': '30px', 'width': '200px', 'font-size': '20px'}
                    ),
                    
                    "Y:",
                    dcc.Dropdown(
                        id='y_attribute',
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
                id='Scatterplot',
                config=cmn.graph_config(),
                figure=scatter_plot(cmn.county_df, attrs[0], attrs[-1], wd=cmn.map_wd)
            ),
        ]
    )