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
              'new_cases_per_100k': {'name': 'New Cases per 100k', 'log': True}, 
              'new_deaths': {'name': 'New Deaths', 'log': True},
              'overall_pct_change': {'name': 'Mobility % Change', 'log': False},
              'Poverty': {'name': '% In Poverty', 'log': False},
              'population': {'name': 'Population', 'log': True},
              'Service': {'name': '% Service Jobs', 'log': False},
              'Production': {'name': '% Production Jobs', 'log': False},
              'dem_gop_diff_16': {'name': 'Rep_vs_Dem Vote 2016', 'log': False},
              'FBFilterBubble': {'name': 'FB Filter Bubble Index', 'log': False},
              
              }

ts_attrs = ['cases', 'cases_per_100k',
            'deaths', 'deaths_per_100k',
            'new_cases', 'new_cases_per_100k',
            'new_deaths', 
            'overall_pct_change']

geo_areas = ['States', 'Counties']
timeseries_mode = ['Country', 'State', 'County']

init_attr = 5   
country_df = state_df = county_df = dates = None 
current_geo = None
current_date_idx = None
current_attr = next(iter(attributes.keys()))
current_ts_mode = timeseries_mode[0]

map_wd = 775
map_ht = 500

filter_wd = 320
ts_wd = 320

scatter_wd = map_wd
#scatter_wd = filter_wd + map_wd


scatterplot_div = filters_div = map_div = ts_div = None


def get_current_data(geo):
    return state_df if geo == geo_areas[0] else county_df
    

def graph_config():
    return {"displaylogo": False,
            'displayModeBar': False
            }


def attribute_selector(id_str, default=None, allow_none=False, ht='38px'):
    options = [{'label': 'None', 'value': 'None'}] if allow_none else []
    options = options + [{'label': attributes[attr]['name'], 'value': attr} for attr in attributes.keys()]
    default_val = 'None' if (allow_none and default is None) else (default or list(iter(attributes.keys()))[init_attr])
    return dcc.Dropdown(
        id=id_str,
        options=options,
        value=default_val,
        searchable=False,
        clearable=False,
        style={'height': ht, 'width': '200px', 'fontSize': '15px'}
    )


def series_as_string(vals):
    return vals.apply(lambda x: str(int(x)) if (type(x) == int or x.is_integer()) else '%.2f'%x)
 