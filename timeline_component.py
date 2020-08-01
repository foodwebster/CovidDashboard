# -*- coding: utf-8 -*-


import dash_core_components as dcc
import dash_html_components as html

import common as cmn

from timeline_plot import timeline_plot, add_timeline

def get_timeline_plot(dates, values, logy):
    return timeline_plot(dates, 
                         values, 
                         logy=logy,
                         title=None)


def get_ts_plot(attr, state, county, logy):
    '''
    plot_type: 0 - pandemic data, 1 - movement data
    one or none of state, county should be set
    '''
    if state is not None:
        sdf = cmn.state_df[cmn.state_df.State == state]
        fig = get_timeline_plot(sdf.index, 
                                 sdf[attr], 
                                 logy,
                                )
        add_timeline(fig, cmn.country_df.index, cmn.country_df[attr])
    elif county is not None:
        cdf = cmn.county_df[cmn.county_df.fips_str == county]
        fig = get_timeline_plot(cdf.index, 
                                 cdf[attr], 
                                 logy,
                                )
        add_timeline(fig, cmn.country_df.index, cmn.country_df[attr])
    else:
        fig = get_timeline_plot(cmn.country_df.index, 
                                 cmn.country_df[attr], 
                                 logy,
                                 )
    return fig


def get_timeline(attr, state, county, show, logy):
    
    if state is not None:
        title = state
    elif county is not None:
        cdf = cmn.county_df[cmn.county_df.fips_str == county]
        title = cdf.iloc[0]['County Name'] + " " + cdf.iloc[0]['State']
    else:
        title = "US"
    line2 = cmn.attributes[attr]['name']
    logy = 'logy' in logy if logy is not None else cmn.attributes[attr]['log']
    return html.Div(
        children=[
            html.Div(children=[
                html.P(title + '   ' + line2),
                dcc.Checklist(
                    id='timeline_logy_' + attr,
                    options=[
                        {'label': 'Log y', 'value': 'logy'},
                    ],
                    value=['logy'] if logy else [],
                    # only display log checkbox for attributes that allow log axis
                    style={'margin-left': '10px', 'margin-right': '10px'} if cmn.attributes[attr]['log'] else {'display': 'none'}
                )],
                className='row',
                style={'display': 'flex',
                       'margin-left': '10px', 
                       'margin-right': '20px', 
                       'line-height': '20px'
                       }
            ),
            dcc.Graph(id='timeline_' + attr,
                      config=cmn.graph_config(),
                      figure=get_ts_plot(attr, state, county, logy),
                      style={'margin-top': '0px'}
            )      
        ],
        style={'display': 'block' if show else 'none', 'margin-top': '10px'}
    )    


def get_timeline_div(attrs, logy=None, state=None, county=None):
    return html.Div(
        id='Timelines',
        children=[
            html.Div(
                children=[
                    html.H3('Timelines', style={
                        'textAlign': 'left',
                        }),
                    html.Button('Reset', 
                                id='timeline_reset', 
                                n_clicks=0, 
                                title='Reset to timeline for the whole US', 
                                style={'marginLeft': 'auto', 'marginTop': '15px', 'fontSize': '12px'})
                ],
                className='row',
                style={'display': 'flex'}
            ),
            dcc.Dropdown(
                id='timeline_attrs',
                options=[{'label': cmn.attributes[val]['name'], 'value': val} for val in cmn.ts_attrs],
                value=attrs,
                searchable=False,
                multi=True,
                placeholder="Select timeline attributes",
                style={'fontSize': '20px'}
            )
        ] + [get_timeline(attr, state, county, attr in attrs, logy[idx] if logy else None) for idx, attr in enumerate(cmn.ts_attrs)],
        style={'width': cmn.ts_wd}
    )
