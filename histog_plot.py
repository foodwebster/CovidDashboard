# -*- coding: utf-8 -*-

import numpy as np
import plotly.graph_objects as go
from plotly.offline import plot


def histog_plot(values, log_bins=False, min_val=None, max_val=None, nbins=100, title=None, ht=150):
    if log_bins:
        values = np.log10(values[values > 0])
    max_val = max_val or 1.01 * values.max()
    min_val = min_val or 0.99 * values.min()
    fig = go.Figure(data=go.Histogram(x=values, 
                                      xbins=dict(
                                              start=min_val,
                                              end=max_val,
                                              size=(max_val - min_val)/nbins),
                                      autobinx=False,
                                      nbinsx=nbins
                                     )
                    )
    if title:
        fig.update_layout(title_text=title)
    fig.update_layout(
        margin=dict(l=20, r=20, t=30, b=10),
        paper_bgcolor="White",
        height=ht
    )
    return fig

if __name__ == "__main__":
    # execute only if run as a script
    from prepare_case_data import get_case_data
    from prepare_movement_data import get_movement_data

    country_case_df, state_case_df, county_case_df = get_case_data()
    country_mmt_df, state_mmt_df, county_mmt_df = get_movement_data()
    attributes = ['cases', 'deaths', 'total_case_rate', 'total_death_rate', 'new_cases', 'new_deaths']
    
    attr = attributes[4]
    fig = histog_plot(country_case_df[attr], nbins=100, log_bins=True)
    fig['data'][0].selectedpoints=[0, 1, 2, 3, 4, 5, 47, 48, 80, 81, 82, 83, 84, 85, 86, 87, 88]
    plot(fig)
