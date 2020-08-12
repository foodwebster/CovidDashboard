# -*- coding: utf-8 -*-

#import json
import dash
import dash_auth
import dash_core_components as dcc
import dash_html_components as html

import common as cmn
from load_data import load_data

from map_component import get_map_div, update_map, update_map_figure
from scatterplot_component import get_scatterplot_div, scatterplot_figure
from filters_component import get_filters_div_horiz
from timeline_component import get_timeline_div

cmn.country_df, cmn.state_df, cmn.county_df, cmn.dates = load_data()

cmn.current_date_idx = len(cmn.dates) - 1


def get_tab_div(divs):
    '''
    build div for tabbed divs
    '''
    # build mapping between index and date display data 
    # only display one date per week, include styling info
    return html.Div(
        children=[
            dcc.Tabs([dcc.Tab(label=title, children=[div]) for title, div in divs.items()]),
        ],
        style={'width': cmn.map_wd, 'marginBottom': 40, 'marginLeft': 10, 'marginRight': 10},
    )


def get_time_filtered_div(div):
    '''
    build div for tabbed plots with time filter slider below the plot
    '''
    # build mapping between index and date display data 
    # only display one date per week, include styling info
    date_ticks = dict(zip(range(len(cmn.dates)), [{'label': str(d.date()),
                                             'style': {"transform": "translate(-45px, 7px) rotate(-45deg)"}
                                             } if d.dayofweek==1 else '' for d in cmn.dates]))
    return html.Div(
        children=[
            div,
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
    global filters_div, map_div, ts_div, scatterplot_div, current_geo
    current_geo = cmn.geo_areas[1]
    filters_div = get_filters_div_horiz([list(iter(cmn.attributes.keys()))[cmn.init_attr]])
    map_div = get_map_div(current_geo)
    ts_div = get_timeline_div([cmn.ts_attrs[cmn.init_attr], cmn.ts_attrs[6]])
    scatterplot_div = get_scatterplot_div(current_geo)
    return html.Div(
        children=[
            html.H1(children='Covid Dashboard', style={
                'textAlign': 'left',
            }),
            html.Div(
                children=[
                    html.Div(
                        children=[
                            get_time_filtered_div(map_div),
                            get_tab_div({'Timeline': ts_div, 'Scatterplot': scatterplot_div})
                        ],
                        className='row',
                        style={'display': 'flex'}
                    ), filters_div
                ]
            )
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
    for div in filters_div.children[1:]:
        if div.id == fid:
            return div
    return None


def get_attr_histog(attr):
    for div in filters_div.children[1:]:
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


# callback to redisplay map and selection based on state/county, attribute, date and filters
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
            # change in map options (state/county, date etc)
            if geo != cmn.current_geo:
                #mapbox_zoom = cur_map['layout'][0].mapbox_zoom
                #mapbox_center = cur_map['layout'][0].mapbox_center
                cur_map = map_div.children[1].figure = update_map(geo, attribute, date_idx)
                #cur_map['layout'][0].mapbox_zoom = mapbox_zoom
                #cur_map['layout'][0].mapbox_center = mapbox_center
            else:
                update_map_figure(cur_map, geo, attribute, date_idx)
        selected = update_filter_values(filter_values)
        # select values in map and scatterplot
        cur_map.data[0]['selectedpoints'] = selected

    return cur_map


# callback for dropdowns to display filters
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
    #return [html.H5("Geo: %s %s"%(geo, json.dumps(ctx.triggered)))] + filters_div.children
    cmn.current_geo = geo
    
    selected = None
    cur_map = map_div.children[1].figure
    if ctx.triggered[0]['prop_id'] != '.':
        # call triggered by a change in UI param
        update_selected_filters(selected_filters)
        #if ctx.triggered[0]['prop_id'] == 'filter_attrs.value':
        #    # change in selected filters
        #    update_selected_filters(selected_filters)
        #elif changed_map_options(ctx):
        #    # new geo, date or attribute, force new filters
        #    filters_div.children = get_filters_div(selected_filters).children
        selected = update_filter_values(filter_values)
        # select values in map and scatterplot
        cur_map.data[0]['selectedpoints'] = selected
    else:
        update_selected_filters(selected_filters)

    return filters_div.children
    #return [html.H5("Geo: %s %s"%(geo, json.dumps(ctx.triggered)))] + filters_div.children
    

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
        ts_div = get_timeline_div(attrs, logy=logy)
    else:
        if cmn.current_geo == cmn.geo_areas[0]:  # states
            click_state = clickData['points'][0]['location'] if clickData else None
            ts_div = get_timeline_div(attrs, state=click_state, logy=logy)
        elif cmn.current_geo == cmn.geo_areas[1]:  # counties
            click_county = clickData['points'][0]['location'] if clickData else None
            ts_div = get_timeline_div(attrs, county=click_county, logy=logy)
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

