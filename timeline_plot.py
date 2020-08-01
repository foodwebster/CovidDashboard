# -*- coding: utf-8 -*-


import plotly.graph_objects as go
from plotly.offline import plot


def timeline_plot(t, values, logy=True, title=None, ht=120):
    fig = go.Figure(data=go.Scatter(x=t, y=values))
    if logy:
        fig.update_layout(yaxis_type="log")
    if title:
        fig.update_layout(title_text=title)
    fig.update_layout(
        margin=dict(l=20, r=20, t=10, b=10),
        paper_bgcolor="White",
        height=ht
    )
    return fig


def add_timeline(fig, t, values):
    fig.add_trace(go.Scatter(x=t, y=values, line={'color': 'lightgray'}))
    fig.update_layout(showlegend=False)
    

if __name__ == "__main__":
    # execute only if run as a script
    from prepare_case_data import get_case_data
    from prepare_movement_data import get_movement_data

    country_case_df, state_case_df, county_case_df = get_case_data()
    country_mmt_df, state_mmt_df, county_mmt_df = get_movement_data()
    attributes = ['cases', 'deaths', 'total_case_rate', 'total_death_rate']
    
    attr = attributes[0]
    data = county_case_df[['fips_str', attr]]
    data = data[data.fips_str == data.fips_str.iloc[0]]
    fig = timeline_plot(data.index, data[attr])
    plot(fig)
