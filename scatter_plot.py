# -*- coding: utf-8 -*-

import numpy as np
import plotly.graph_objects as go
from plotly.offline import plot

def scatter_plot(df, xattr, yattr, szattr=None, colorattr=None, logx=False, logy=False, title=None, ht=600):
    x_vals = df[xattr]
    y_vals = df[yattr]
    fig = go.Figure(data=go.Scatter(x=x_vals, 
                                    y=y_vals, 
                                    mode='markers')
                                   )
    if title:
        fig.update_layout(title_text=title)
    if logx:
        fig.update_layout(xaxis_type="log")
    if logy:
        fig.update_layout(yaxis_type="log")
    fig.update_layout(
        margin=dict(l=20, r=20, t=30, b=10),
        paper_bgcolor="White",
        height=ht
    )
    return fig

if __name__ == "__main__":
    # execute only if run as a script
    from load_data import load_data

    country_df, state_df, county_df, dates = load_data()

    attributes = ['cases', 'deaths', 'total_case_rate', 'total_death_rate', 'new_cases', 'new_deaths', 'overall_pct_change']
    
    attr = attributes[-1]
    values = state_df[attr].loc[dates[-1]]
    fig = scatter_plot(county_df.loc[dates[-1]], attributes[0], attributes[-1], logx=True)
    plot(fig)
