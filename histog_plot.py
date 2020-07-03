# -*- coding: utf-8 -*-

import numpy as np
import plotly.graph_objects as go
from plotly.offline import plot

def histog_plot(values, log_bins=False, min_val=None, max_val=None, nbins=100, xlabel=None, title=None, ht=150):
    if log_bins:
        values = np.log10(values[values > 0])
    range_val = values.max() - values.min()
    max_val = max_val or values.max() + 0.01*range_val
    min_val = min_val or values.min() - 0.01*range_val
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
    if xlabel:
        fig.update_layout(xaxis_title_text=xlabel)
    fig.update_layout(
        margin=dict(l=20, r=20, t=10, b=10, pad=5),
        paper_bgcolor="White",
        height=ht,
        xaxis=dict(title=dict(text=xlabel, standoff=5), automargin=True)
    )
    return fig

if __name__ == "__main__":
    # execute only if run as a script
    from load_data import load_data

    country_df, state_df, county_df, dates = load_data()

    attributes = ['cases', 'deaths', 'total_case_rate', 'total_death_rate', 'new_cases', 'new_deaths', 'overall_pct_change']
    
    attr = attributes[-1]
    values = state_df[attr].loc[dates[-1]]
    fig = histog_plot(values, nbins=100, log_bins=False)
    fig['data'][0].selectedpoints=[32, 1, 36, 9, 10, 41, 48, 18, 19, 21, 22, 23, 24, 26, 28]
    plot(fig)
