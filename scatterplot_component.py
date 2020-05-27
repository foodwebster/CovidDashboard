# -*- coding: utf-8 -*-

import dash_core_components as dcc
import dash_html_components as html

import common as cmn
from scatter_plot import scatter_plot

def get_scatterplot_div():
    text_style = {'margin-left': '10px', 'margin-right': '10px', 'line-height': '38px'}
    attrs = list(cmn.attributes.keys())
    return html.Div(
        children=[
            html.Div(
                id='scatterplot_controls',
                children=[
                    html.Div(
                        children=[
                            html.P("X:", style={'margin-left': '29px', 'margin-right': '10px', 'line-height': '38px'}),
                            cmn.attribute_selector('x_attribute'),                    
                            html.P("Y:", style={'margin-left': '38px', 'margin-right': '10px', 'line-height': '38px'}),
                            cmn.attribute_selector('y_attribute', default=attrs[-1]),
                            dcc.Checklist(
                                id='log_axes',
                                options=[
                                    {'label': 'Log x', 'value': 'logx'},
                                    {'label': 'Log y', 'value': 'logy'},
                                ],
                                value=[],
                                style={'margin-left': '10px', 'margin-right': '10px'}
                            ),
                        ],
                        className='row',
                        style={'display': 'flex'}
                    ),
                    html.Div(
                        children=[
                            html.P("Size:", style=text_style),
                            cmn.attribute_selector('size_attribute', allow_none=True),
                            html.P("Color:", style=text_style),
                            cmn.attribute_selector('color_attribute', allow_none=True),
                        ],
                        className='row',
                        style={'display': 'flex'}
                    )
                ],
                style={'margin-top': '5px'}
            ),
            dcc.Graph(
                id='Scatterplot',
                config=cmn.graph_config(),
                figure=scatterplot_figure(attrs[0], attrs[-1], None, None, False, False)
            ),
        ],
        #style={"border-top":"1px black solid", 'width': cmn.scatter_wd}
    )


def scatterplot_figure(xattr, yattr, colorattr, sizeattr, logx, logy, geo=None, date_idx=None):
    df = cmn.get_current_data(geo)
    df = df[df.index == cmn.dates[date_idx or cmn.current_date_idx]]
    return scatter_plot(df, xattr, yattr,
                        szattr=sizeattr, colorattr=colorattr,
                        logx=logx, logy=logy,
                        wd=cmn.scatter_wd)

