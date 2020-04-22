# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %%
# Setting up the environment.
import numpy as np
import pandas as pd
from scipy import stats
import plotly as pl


# %%
# Load the data from the John Hopkins github repo
df = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports_us/04-20-2020.csv')

    # %%
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

levels = ['County/State', 'State'] # levels totaled for the hierarchical chart
color_columns = 'Deaths'
value_column = 'Confirmed'

def build_hierarchical_dataframe(df, levels, value_column, color_columns=None):
    """
    Build a hierarchy of levels for Sunburst or Treemap charts.

    Levels are given starting from the bottom to the top of the hierarchy,
    ie the last level corresponds to the root.
    """
    df_all_trees = pd.DataFrame(columns=['id', 'parent', 'value', 'color'])
    for i, level in enumerate(levels):
        df_tree = pd.DataFrame(columns=['id', 'parent', 'value', 'color'])
        dfg = df.groupby(levels[i:]).sum()
        dfg = dfg.reset_index()
        df_tree['id'] = dfg[level].copy()
        if i < len(levels) - 1:
            df_tree['parent'] = dfg[levels[i+1]].copy()
        else:
            df_tree['parent'] = 'total'
        df_tree['value'] = dfg[value_column]
        df_tree['color'] = dfg[color_columns]
        df_all_trees = df_all_trees.append(df_tree, ignore_index=True)
    total = pd.Series(dict(id='total', parent='',
                              value=df[value_column].sum(),
                              color=df[color_columns].sum()
                              ))
    df_all_trees = df_all_trees.append(total, ignore_index=True)
    return df_all_trees

df_all_trees = build_hierarchical_dataframe(df1, levels, value_column, color_columns)
avg = df1['Confirmed'].mean()

fig = make_subplots(1, 1, specs=[[{"type": "domain"}]])

fig.add_trace(go.Treemap(
    labels=df_all_trees['id'],
    parents=df_all_trees['parent'],
    values=df_all_trees['value'],
    branchvalues='total',
    marker=dict(
        colors=df_all_trees['color'],
        colorscale='matter',
        cmid=avg),
    hovertemplate='<b>%{label} </b> <br> Confirmed: %{value:,.2s}<br> Deaths: %{color:,.2s}<br> %{percentParent:,2f}',
    texttemplate='<b>%{label} </b> <br> Confirmed: %{value:,.2s} <br> %{percentParent} of state total',
    maxdepth=3,
    ), 1, 1)

fig.update_layout(margin=dict(t=0, b=0, r=0, l=0))
fig.show()

import plotly.io as pio
pio.write_html(fig, file='Index.html', auto_open=True)

# %%
codes = pd.factorize(df1['State'])



#df_all_trees['State Codes'] = codes


# %%
