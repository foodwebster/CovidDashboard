# -*- coding: utf-8 -*-

import json
import pandas as pd

import dash
import dash_auth
import dash_core_components as dcc
import dash_html_components as html

import common as cmn
from county_plot import county_plot
from state_plot import state_plot
from timeline_plot import timeline_plot
from histog_plot import histog_plot


def load_data():
    country_df = pd.read_csv(cmn.datapath/"CountryData.csv", parse_dates=['date']).set_index('date')
    state_df = pd.read_csv(cmn.datapath/"StateData.csv", parse_dates=['date']).set_index('date')
    county_df = pd.read_csv(cmn.datapath/"CountyData.csv", parse_dates=['date']).set_index('date')                           
    dates = country_df.index.unique().to_list()
    return country_df, state_df, county_df, dates


country_df, state_df, county_df, dates = load_data()

# build mapping between index and date display data 
# only display one date per week, include styling info
date_idx = dict(zip(range(len(dates)), [{'label': str(d.date()),
                                         'style': {"transform": "translate(-45px, 7px) rotate(-45deg)"}
                                         } if d.dayofweek==1 else '' for d in dates]))

# list of data attributes
attributes = {'cases': {'name': 'Cases', 'log': True}, 
              'deaths': {'name': 'Deaths', 'log': True},
              'cases_per_100k': {'name': 'Cases per 100k', 'log': True}, 
              'deaths_per_100k': {'name': 'Deaths per 100k', 'log': True},
              'new_cases': {'name': 'New Cases', 'log': True},
              'new_deaths': {'name': 'New Deaths', 'log': True},
              'overall_pct_change': {'name': 'Mobility % Change', 'log': False},
              }

ts_attrs = ['cases', 'deaths', 'new_cases', 'new_deaths', 'overall_pct_change']

geo_areas = ['States', 'Counties']
timeseries_mode = ['Country', 'State', 'County']
    
current_geo = geo_areas[0]
current_date_idx = len(dates) - 1
current_attr = next(iter(attributes.keys()))
current_ts_mode = timeseries_mode[0]

map_wd = 800

filters_div = map_div = ts_div = None


def graph_config():
    return {"displaylogo": False,
            'displayModeBar': False
            }


def get_county_plot_data(attr, date_idx):
    data = county_df[['fips_str', attr]]
    # get max, min before selecting desired date, so color scale is invariant
    data_max = data[attr].max()
    data_min = data[attr].min()
    data = data.loc[dates[date_idx]]
    return data, data_max, data_min


def get_county_plot(attr, date_idx, wd):
    data, data_max, data_min = get_county_plot_data(attr, date_idx)
    return county_plot(data[attr], data['fips_str'], data_max, data_min, attributes[attr]['log'], "Covid-19 Data", wd=wd)


def get_state_plot_data(attr, date_idx):
    data = state_df[['State', attr]]
    data_max = data[attr].max()
    data_min = data[attr].min()
    data = data.loc[dates[date_idx]]
    return data, data_max, data_min


def get_state_plot(attr, date_idx, wd):
    data, data_max, data_min = get_state_plot_data(attr, date_idx)
    return state_plot(data[attr], data['State'], data_max, data_min, attributes[attr]['log'], "Covid-19 Data", wd=wd)


def get_map_plot(geo, attr, date_idx, wd):
    global current_attr
    current_attr = attr
    global current_date_idx
    current_date_idx = date_idx
    global current_geo
    current_geo = geo

    if geo == geo_areas[0]:
        fig = get_state_plot(attr, date_idx, wd)
    else:
        fig = get_county_plot(attr, date_idx, wd)
    return fig


def get_timeline_plot(dates, values, logy, title):
    return timeline_plot(dates, 
                         values, 
                         logy=logy,
                         title=title)


def get_ts_plot(attr, state, county):
    '''
    plot_type: 0 - pandemic data, 1 - movement data
    one or none of state, county should be set
    '''
    logy = attributes[attr]['log']
    if state is not None:
        sdf = state_df[state_df.State == state]
        return get_timeline_plot(sdf.index, 
                                 sdf[attr], 
                                 logy,
                                 state + " " + attributes[attr]['name']
                                )
    elif county is not None:
        cdf = county_df[county_df.fips_str == county]
        return get_timeline_plot(cdf.index, 
                                 cdf[attr], 
                                 logy,
                                 county + " " + attributes[attr]['name']
                                )
    else:
        return get_timeline_plot(country_df.index, 
                                 country_df[attr], 
                                 logy,
                                 "US " + attributes[attr]['name']
                                 )

def get_histog_plot(attr, date_idx, state, county):
    '''
    plot histogram of the data shown in the map
    '''
    global current_geo
    if current_geo == geo_areas[0]:
        data = state_df.loc[dates[date_idx]]
        return histog_plot(data[attr], title=attributes[attr]['name'])
    else:
        data = county_df.loc[dates[date_idx]]
        return histog_plot(data[attr], title=attributes[attr]['name'])


def get_map_div():
    return html.Div(
        children=[
            html.Div(
                children=[
                    dcc.Dropdown(
                        id='geo',
                        options=[{'label': val, 'value': val} for val in geo_areas],
                        value=geo_areas[0],
                        searchable=False,
                        clearable=False,
                        style={'height': '40px', 'width': '150px', 'fontSize': '20px'}
                    ),
                    dcc.Dropdown(
                        id='attribute',
                        options=[{'label': attributes[attr]['name'], 'value': attr} for attr in attributes.keys()],
                        value=next(iter(attributes.keys())),
                        searchable=False,
                        clearable=False,
                        style={'height': '40px', 'width': '300px', 'font-size': '20px'}
                    ),
                ],
                className='row',
                style={'display': 'flex'}
            ),
            dcc.Graph(
                id='Map',
                config=graph_config(),
                figure=get_map_plot(geo_areas[0], next(iter(attributes.keys())), len(dates) - 1, map_wd)
            ),
            dcc.Slider(
                id='date_slider',
                updatemode='mouseup',
                min=0,
                max=len(dates) - 1,
                step=None,
                marks=date_idx,
                value=len(dates) - 1
            )
        ],
        style={'width': map_wd}
    )


def get_filter(attr, date_idx, state, county, enable=True):
    histog = get_histog_plot(attr, date_idx, state, county)
    nbins = histog['data'][0].nbinsx
    return html.Div(
        id='filter_'+attr,
        children=[
            dcc.Graph(
                id='filter_histog_' + attr,
                config=graph_config(),
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
        style={'width': 400,
               'display': 'block' if enable else 'none'
              }  
    )    

def get_timeseries_div(attrs, state=None, county=None):
    return html.Div(
        id='Timelines',
        children=[
            html.H3('Timelines', style={
                'textAlign': 'left',
            }),
            dcc.Dropdown(
                id='timeline_attrs',
                options=[{'label': val, 'value': val} for val in ts_attrs],
                value=attrs,
                searchable=False,
                multi=True,
                placeholder="Select timeline attributes",
                style={'fontSize': '20px'}
            )] + [dcc.Graph(id='timeline_' + attr,
                            config=graph_config(),
                            figure=get_ts_plot(attr, state, county),
                            style={'display': 'block' if attr in attrs else 'none'}) for attr in ts_attrs],
        style={'width': 400}
    )


def get_filters_div(selected_filters=[], state=None, county=None):
    return html.Div(
        id='Filters',
        children=[
            html.H3('Filters', style={
                'textAlign': 'left',
            }),
            dcc.Dropdown(
                id='filter_attrs',
                options=[{'label': val, 'value': val} for val in attributes.keys()],
                value=next(iter(attributes.keys())),
                searchable=False,
                multi=True,
                placeholder="Select filter attributes",
                style={'fontSize': '20px'}
            ),
        ] + [get_filter(attr, current_date_idx, state, county, attr in selected_filters) for attr in attributes.keys()],
        style={'width': 400}
    )


def get_app_layout():
    global filters_div, map_div, ts_div
    filters_div = get_filters_div([[next(iter(attributes.keys()))]])
    map_div = get_map_div()
    ts_div = get_timeseries_div([ts_attrs[0], ts_attrs[-1]])
    return html.Div(
        children=[
            html.H1(children='Covid Dashboard', style={
                'textAlign': 'left',
            }),
            html.Div(
                children=[
                    filters_div,
                    map_div,
                    ts_div
                ],
                className='row',
                style={'display': 'flex'}
            )
        ]
    )


# Keep this out of source code repository - save in a file or a database
VALID_USERNAME_PASSWORD_PAIRS = {
    'user': 'woot'
}

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash()
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


def update_map(geo, attribute, date_idx):
    attr = attribute or next(iter(attributes.keys()))
    geo = geo or geo_areas[0]
    return get_map_plot(geo, attr, date_idx, map_wd)


def update_filter_values(*values):
    #print("updating filters %s"%str(values))
    global filters_div
    selected = None
    for idx, attr in enumerate(attributes.keys()):
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
    for attr in attributes.keys():
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
    for attr in ts_attrs:
        div = get_attr_timeseries(attr)
        new_val = 'block' if attr in values else 'none'
        if div.style['display'] != new_val:
            # filter viz changed
            div.style['display'] = new_val
    # retain values in multi-select
    ts_div.children[1].value = values


# callback for dropdowns and slider to display correct map (state/county, attribute, date)
@app.callback(
    [dash.dependencies.Output('Map', 'figure'),
     dash.dependencies.Output('Filters', 'children')],
    [
        dash.dependencies.Input('geo', 'value'),
        dash.dependencies.Input('attribute', 'value'),
        dash.dependencies.Input('date_slider', 'value'),
        dash.dependencies.Input('filter_attrs', 'value'),
    ] + [dash.dependencies.Input('filter_slider_'+attr, 'value') for attr in attributes.keys()]
    )
def update_all(geo, attribute, date_idx, selected_filters, *filter_values):

    def changed_filter_values(ctx):
        changed = ctx.triggered[0]['prop_id']
        ids = ['filter_slider_'+attr+'.value' for attr in attributes.keys()]
        return changed in ids
    
    def changed_map_options(ctx):
        changed = ctx.triggered[0]['prop_id']
        ids = [val+'.value' for val in ['geo', 'attribute', 'date_slider']]
        return changed in ids    
    
    global filters_div
    ctx = dash.callback_context
    
    cur_map = map_div.children[1].figure
    if ctx.triggered[0]['prop_id'] != '.':
        # call triggered by a change in UI param
        selected = None
        if ctx.triggered[0]['prop_id'] == 'filter_attrs.value':
            # change in selected filters
            update_selected_filters(selected_filters)
        elif changed_map_options(ctx):
            # change in map options (state/county, date etc)
            map_div.children[1].figure = update_map(geo, attribute, date_idx)
            # new geo, date or attribute, force new filter
            filters_div = get_filters_div(selected_filters)
        elif changed_filter_values(ctx):
            # change in filter slider value
            selected = update_filter_values(filter_values)
        # select values in map
        cur_map.data[0]['selectedpoints'] = selected
    else:
        update_selected_filters(selected_filters)

    return cur_map, filters_div.children
    #return cur_map, [html.H5("selecting filters %s  triggered: %s"%(str(selected_filters), json.dumps(ctx.triggered)))] + filters_div.children


# callback to respond to map click
@app.callback(
    dash.dependencies.Output('Timelines', 'children'),
    [dash.dependencies.Input('Map', 'clickData'),
     dash.dependencies.Input('timeline_attrs', 'value')])
def process_timeline_changes(clickData, value):
    global ts_div
    if current_geo == geo_areas[0]:  # states
        click_state = clickData['points'][0]['location'] if clickData else None
        ts_div = get_timeseries_div(value, state=click_state)
    elif current_geo == geo_areas[1]:  # counties
        click_county = clickData['points'][0]['location'] if clickData else None
        ts_div = get_timeseries_div(value, county=click_county)
    else:
        update_selected_timelines(value)
    return ts_div
    #return json.dumps(clickData, indent=2)


if __name__ == '__main__':
    app.run_server(debug=True)

