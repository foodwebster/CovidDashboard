# -*- coding: utf-8 -*-

import json
import dash
import dash_auth
import dash_core_components as dcc
import dash_html_components as html

import common as cmn
from load_data import load_data
from timeline_plot import timeline_plot
from histog_plot import histog_plot

from map_component import get_map_div, update_map, update_map_figure
from scatterplot_component import get_scatterplot_div, scatterplot_figure

cmn.country_df, cmn.state_df, cmn.county_df, cmn.dates = load_data()

cmn.current_date_idx = len(cmn.dates) - 1


def get_timeline_plot(dates, values, logy):
    values = values.fillna(values.mean())
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
        return get_timeline_plot(sdf.index, 
                                 sdf[attr], 
                                 logy,
                                )
    elif county is not None:
        cdf = cmn.county_df[cmn.county_df.fips_str == county]
        return get_timeline_plot(cdf.index, 
                                 cdf[attr], 
                                 logy,
                                )
    else:
        return get_timeline_plot(cmn.country_df.index, 
                                 cmn.country_df[attr], 
                                 logy,
                                 )

def get_timeline(attr, state, county, show, logy):
    
    if state is not None:
        title = state + " - " + cmn.attributes[attr]['name']
    elif county is not None:
        cdf = cmn.county_df[cmn.county_df.fips_str == county]
        title = cdf.iloc[0]['County Name'] + " " + cdf.iloc[0]['State'] + ' - ' + cmn.attributes[attr]['name']
    else:
        title = "US - " + cmn.attributes[attr]['name']
    logy = 'logy' in logy if logy is not None else cmn.attributes[attr]['log']
    return html.Div(
        children=[
            html.Div(children=[
                        html.P(title, style={'margin-left': '10px', 'margin-right': '20px', 'line-height': '20px'}),
                        dcc.Checklist(
                            id='timeline_logy_' + attr,
                            options=[
                                {'label': 'Log y', 'value': 'logy'},
                            ],
                            value=['logy'] if logy else [],
                            # only display log checkbox for attributes that allow log axis
                            style={'margin-left': '10px', 'margin-right': '10px'} if cmn.attributes[attr]['log'] else {'display': 'none'}
                        ), 
                     ],
                     className='row',
                     style={'display': 'flex'}
            ),
            dcc.Graph(id='timeline_' + attr,
                      config=cmn.graph_config(),
                      figure=get_ts_plot(attr, state, county, logy),
                      style={'margin-top': '0px'}
            )      
        ],
        style={'display': 'block' if show else 'none', 'margin-top': '10px'}
    )    

def get_histog_plot(attr, date_idx, state, county):
    '''
    plot histogram of the data shown in the map
    '''
    if cmn.current_geo == cmn.geo_areas[0]:
        data = cmn.state_df.loc[cmn.dates[date_idx]]
    else:
        data = cmn.county_df.loc[cmn.dates[date_idx]]
    values = data.loc[~data[attr].isnull().to_numpy(), attr]
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

def get_timeseries_div(attrs, logy=None, state=None, county=None):
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
                                title='Reset to US timeline', 
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


def get_time_filtered_tab_div(divs):
    '''
    build div for tabbed plots with time filter slider below the plots
    '''
    # build mapping between index and date display data 
    # only display one date per week, include styling info
    date_ticks = dict(zip(range(len(cmn.dates)), [{'label': str(d.date()),
                                             'style': {"transform": "translate(-45px, 7px) rotate(-45deg)"}
                                             } if d.dayofweek==1 else '' for d in cmn.dates]))
    return html.Div(
        children=[
            dcc.Tabs([dcc.Tab(label=title, children=[div]) for title, div in divs.items()]),
            dcc.Slider(
                id='date_slider',
                updatemode='mouseup',
                min=0,
                max=len(cmn.dates) - 1,
                step=None,
                marks=date_ticks,
                value=len(cmn.dates) - 1,
            )
        ],
        style={'width': cmn.map_wd, 'marginBottom': 40, 'marginLeft': 10, 'marginRight': 10},
    )


def get_app_layout():
    global filters_div, map_div, ts_div, scatterplot_div
    filters_div = get_filters_div([next(iter(cmn.attributes.keys()))])
    map_div = get_map_div()
    ts_div = get_timeseries_div([cmn.ts_attrs[0], cmn.ts_attrs[-1]])
    scatterplot_div = get_scatterplot_div()
    return html.Div(
        children=[
            html.H1(children='Covid Dashboard', style={
                'textAlign': 'left',
            }),
            html.Div(
                children=[
                    filters_div,
                    get_time_filtered_tab_div({'Map': map_div, 'Scatterplot': scatterplot_div}),
                    ts_div
                ],
                className='row',
                style={'display': 'flex'}
            ),
        ]
    )


# Keep this out of source code repository - save in a file or a database
VALID_USERNAME_PASSWORD_PAIRS = {
    'user': 'woot'
}

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

auth = dash_auth.BasicAuth(
    app,
    VALID_USERNAME_PASSWORD_PAIRS
)

app.layout = get_app_layout()

server = app.server     # needed for gunicorn/heroku deployment
#########################################################################################
#
# app callback handlers and helpers
#
def get_attr_timeseries(attr):
    fid = 'timeline_' + attr
    for div in ts_div.children[2:]:
        if div.id == fid:
            return div
    return None


def get_attr_filter(attr):
    fid = 'filter_' + attr
    for div in filters_div.children[2:]:
        if div.id == fid:
            return div
    return None


def get_attr_histog(attr):
    for div in filters_div.children[2:]:
        if div.style['display'] != 'none':
            for child in div.children:
                if hasattr(child, 'id') and child.id == 'filter_histog_' + attr:
                    return child
    return None


def get_attr_slider(attr):
    for div in filters_div.children[2:]:
        if div.style['display'] != 'none':
            for child in div.children:
                if hasattr(child, 'id') and child.id == 'filter_slider_' + attr:
                    return child
    return None


def update_filter_values(*values):
    '''
    get selected items given the filter values
    '''
    #print("updating filters %s"%str(values))
    global filters_div
    selected = None
    for idx, attr in enumerate(cmn.attributes.keys()):
        value = values[0][idx]
        fdiv = get_attr_histog(attr)
        
        if fdiv is not None:
            # select datapoints
            bins = fdiv.figure.data[0].xbins
            min_val = bins.start + value[0] * bins.size
            max_val = bins.start + value[1] * bins.size
            fdiv.figure.data[0]['selectedpoints'] = [idx for idx, val in enumerate(fdiv.figure.data[0].x) if val >= min_val and val <= max_val]    
            new_selected = set(fdiv.figure.data[0]['selectedpoints'])
            # retain slider value
            get_attr_slider(attr).value = value
            selected = new_selected if selected is None else (selected & new_selected)
    return None if selected is None else list(selected)


def update_selected_filters(values):
    global filters_div
    for attr in cmn.attributes.keys():
        div = get_attr_filter(attr)
        new_val = 'block' if attr in values else 'none'
        if div.style['display'] != new_val:
            # filter viz changed
            div.style['display'] = new_val
            # reset filter to defaults
            sl = div.children[1]
            sl.value = [sl.min, sl.max]
            div.children[0].selected = None
    # retain values in multi-select
    filters_div.children[1].value = values


def update_selected_timelines(values):
    global ts_div
    for attr in cmn.ts_attrs:
        div = get_attr_timeseries(attr)
        new_val = 'block' if attr in values else 'none'
        if div.style['display'] != new_val:
            # filter viz changed
            div.style['display'] = new_val
    # retain values in multi-select
    ts_div.children[1].value = values


def changed_filter_values(ctx):
    changed = ctx.triggered[0]['prop_id']
    ids = ['filter_slider_'+attr+'.value' for attr in cmn.attributes.keys()]
    return changed in ids
    

def changed_map_options(ctx):
    '''
    return True if map data (geo, attribute, date) changed by user action
    '''
    changed = ctx.triggered[0]['prop_id']
    ids = [val+'.value' for val in ['geo', 'attribute', 'date_slider']]
    return changed in ids    


# callback to redisplay map and selection
@app.callback(
    dash.dependencies.Output('Map', 'figure'),
    [
        dash.dependencies.Input('geo', 'value'),
        dash.dependencies.Input('attribute', 'value'),
        dash.dependencies.Input('date_slider', 'value'),
        dash.dependencies.Input('filter_attrs', 'value'),
    ] + [dash.dependencies.Input('filter_slider_'+attr, 'value') for attr in cmn.attributes.keys()]
    )
def update_map_plot(geo, attribute, date_idx, selected_filters, *filter_values):    
    global filters_div
    ctx = dash.callback_context
    
    selected = None
    cur_map = map_div.children[1].figure
    if ctx.triggered[0]['prop_id'] != '.':
        if changed_map_options(ctx):
            #mapbox_zoom = cur_map['layout'][0].mapbox_zoom
            #mapbox_center = cur_map['layout'][0].mapbox_center
            # change in map options (state/county, date etc)
            if geo != cmn.current_geo:
                cur_map = map_div.children[1].figure = update_map(geo, attribute, date_idx)
            else:
                update_map_figure(cur_map, geo, attribute, date_idx)
            #cur_map['layout'][0].mapbox_zoom = mapbox_zoom
            #cur_map['layout'][0].mapbox_center = mapbox_center
        selected = update_filter_values(filter_values)
        # select values in map and scatterplot
        cur_map.data[0]['selectedpoints'] = selected

    return cur_map


# callback for dropdowns display correct map (state/county, attribute, date), date and filters
@app.callback(
    dash.dependencies.Output('Filters', 'children'),
    [
        dash.dependencies.Input('geo', 'value'),
        dash.dependencies.Input('date_slider', 'value'),
        dash.dependencies.Input('filter_attrs', 'value'),
    ] + [dash.dependencies.Input('filter_slider_'+attr, 'value') for attr in cmn.attributes.keys()]
    )
def update_filters(geo, date_idx, selected_filters, *filter_values):
    global filters_div
    ctx = dash.callback_context
    
    selected = None
    cur_map = map_div.children[1].figure
    if ctx.triggered[0]['prop_id'] != '.':
        # call triggered by a change in UI param
        if ctx.triggered[0]['prop_id'] == 'filter_attrs.value':
            # change in selected filters
            update_selected_filters(selected_filters)
        elif changed_map_options(ctx):
            # new geo, date or attribute, force new filters
            filters_div = get_filters_div(selected_filters)
        #elif changed_filter_values(ctx):
            # change in filter slider value
        selected = update_filter_values(filter_values)
        # select values in map and scatterplot
        cur_map.data[0]['selectedpoints'] = selected
    else:
        update_selected_filters(selected_filters)

    return filters_div.children
    #return [html.H5("%s, filters: %s, values: %s"%(json.dumps(ctx.triggered), str(selected_filters), str(filter_values)))] + filters_div.children


# callback to update timelines in response to map click or reset button
@app.callback(
    dash.dependencies.Output('Timelines', 'children'),
    [dash.dependencies.Input('Map', 'clickData'),
     dash.dependencies.Input('timeline_attrs', 'value'),
     dash.dependencies.Input('timeline_reset', 'n_clicks')] +
    [dash.dependencies.Input('timeline_logy_'+attr, 'value') for attr in cmn.ts_attrs])
def process_timeline_changes(clickData, attrs, reset, *logy):
    global ts_div
    ctx = dash.callback_context
    if ctx.triggered[0]['prop_id'] == 'timeline_reset.n_clicks':
        ts_div = get_timeseries_div(attrs, logy=logy)
    else:
        if cmn.current_geo == cmn.geo_areas[0]:  # states
            click_state = clickData['points'][0]['location'] if clickData else None
            ts_div = get_timeseries_div(attrs, state=click_state, logy=logy)
        elif cmn.current_geo == cmn.geo_areas[1]:  # counties
            click_county = clickData['points'][0]['location'] if clickData else None
            ts_div = get_timeseries_div(attrs, county=click_county, logy=logy)
        else:
            update_selected_timelines(attrs)
    return ts_div

# scatterplot callbacks
@app.callback(
    dash.dependencies.Output('Scatterplot', 'figure'),
    [
        dash.dependencies.Input('x_attribute', 'value'),
        dash.dependencies.Input('y_attribute', 'value'),
        dash.dependencies.Input('color_attribute', 'value'),
        dash.dependencies.Input('size_attribute', 'value'),
        dash.dependencies.Input('log_axes', 'value'),
        dash.dependencies.Input('geo', 'value'),
        dash.dependencies.Input('date_slider', 'value'),
    ] + [dash.dependencies.Input('filter_slider_'+attr, 'value') for attr in cmn.attributes.keys()]
    )
def update_scatter(xattr, yattr, colorattr, sizeattr, logxy, geo, date_idx, *filter_values):
    logx = 'logx' in logxy
    logy = 'logy' in logxy
    if colorattr == 'None':
        colorattr = None
    if sizeattr == 'None':
        sizeattr = None
    fig = scatterplot_div.children[1].figure = scatterplot_figure(xattr, yattr, 
                                                                  colorattr, sizeattr, 
                                                                  logx, logy, 
                                                                  geo, date_idx)
    # change in filter slider value
    selected = update_filter_values(filter_values)
    fig.data[0]['selectedpoints'] = selected
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)

