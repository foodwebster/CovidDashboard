# -*- coding: utf-8 -*-

import pathlib as pl

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
current_geo = geo_areas[0]
current_date_idx = None
current_attr = next(iter(attributes.keys()))
current_ts_mode = timeseries_mode[0]

map_wd = 800

filters_div = map_div = ts_div = None


def graph_config():
    return {"displaylogo": False,
            'displayModeBar': False
            }


