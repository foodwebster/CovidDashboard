# -*- coding: utf-8 -*-

import pathlib as pl
import dash_core_components as dcc

datapath = pl.Path('data')


# list of data attributes
attributes = {'cases': {'name': 'Cases', 'log': True}, 
              'deaths': {'name': 'Deaths', 'log': True},
              'cases_per_100k': {'name': 'Cases per 100k', 'log': True}, 
              'deaths_per_100k': {'name': 'Deaths per 100k', 'log': True},
              'new_cases': {'name': 'New Cases', 'log': True},
              'new_deaths': {'name': 'New Deaths', 'log': True},
              'overall_pct_change': {'name': 'Mobility % Change', 'log': False},
              'Poverty': {'name': 'Poverty %', 'log': False},
              }

ts_attrs = ['cases', 'deaths', 'new_cases', 'new_deaths', 'overall_pct_change']

geo_areas = ['States', 'Counties']
timeseries_mode = ['Country', 'State', 'County']
   
country_df = state_df = county_df = dates = None 
current_geo = geo_areas[1]
current_date_idx = None
current_attr = next(iter(attributes.keys()))
current_ts_mode = timeseries_mode[0]

map_wd = 800
map_ht = 500

filter_wd = 400
ts_wd = 400

scatter_wd = filter_wd + map_wd


scatterplot_div = filters_div = map_div = ts_div = None


def get_current_data(geo=None):
    geo = geo or current_geo
    if geo == geo_areas[0]:
        df = state_df
    else:
        df = county_df
    return df
    

def graph_config():
    return {"displaylogo": False,
            'displayModeBar': False
            }


def attribute_selector(id_str, default=None, allow_none=False, ht='38px'):
    options = [{'label': 'None', 'value': 'None'}] if allow_none else []
    options = options + [{'label': attributes[attr]['name'], 'value': attr} for attr in attributes.keys()]
    default_val = 'None' if (allow_none and default is None) else (default or next(iter(attributes.keys())))
    return dcc.Dropdown(
        id=id_str,
        options=options,
        value=default_val,
        searchable=False,
        clearable=False,
        style={'height': ht, 'width': '200px', 'font-size': '15px'}
    )
