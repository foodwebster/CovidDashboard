# -*- coding: utf-8 -*-

from urllib.request import urlopen
import json
import numpy as np

import plotly.graph_objects as go
from plotly.offline import plot

with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
    counties = json.load(response)

def county_time_plot(data_by_date, loc, attr, data_max, data_min, title, wd=1000, ht=600):
    traces = []
    for idx, data_locs in enumerate(data_by_date):
        if idx % 100 == 0:
            print("Adding %d"%idx)
        data = data_locs[attr]
        locs = data_locs[loc]
        min_val = data.min()/10.0 or 1.0
        log_data = np.log10(data + min_val)
        log_max = np.log10(data_max + min_val)
        log_min = np.log10(data_min + min_val)
        traces.append(go.Choroplethmapbox(z=log_data, geojson=counties, locations=locs,
                                           colorscale="Viridis",
                                           zmin=log_min,
                                           zmax=log_max,
                                           marker_opacity=0.5,
                                           visible=True, 
                                           text=data
                                          ))
    
    fig = go.Figure()
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    fig.add_trace(traces[-1])
    fig.update_layout(mapbox_style="carto-positron",
                      mapbox_zoom=3, mapbox_center = {"lat": 37.0902, "lon": -95.7129},
                      width=wd, height=ht)
    fig.update_layout(title_text=title)
    return fig


if __name__ == "__main__":
    # execute only if run as a script
    from prepare_case_data import get_case_data

    country_case_df, state_case_df, county_case_df = get_case_data()

    attributes = ['cases', 'deaths', 'total_case_rate', 'total_death_rate']    
    attr = attributes[0]
    data = county_case_df[['fips_str', attr]]
    #data_by_date = [data.loc[idx] for idx in data.loc[data.index]]
    data_by_date = [grp[1] for grp in county_case_df.groupby(level=0)]
    fig = county_time_plot(data_by_date, 'fips_str', attr, data[attr].max(), data[attr].min(), "Covid-19 Cases")
    plot(fig)
