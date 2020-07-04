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
df = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/07-02-2020.csv')


# %%
# Dropping some columns and sorting

df1 = df[["Admin2", "Province_State", "Country_Region", "Confirmed", "Deaths", "Combined_Key"]] #getting the columns I want
df1 = df1[(df1["Country_Region"] == "US")] #dropping countries other than the US
df1 = df1.rename(columns={'Province_State': 'State'})
df1 = df1.rename(columns={'Admin2': 'County'})
df1 = df1.rename(columns={'Country_Region': 'Country'})
df1 = df1.rename(columns={'Combined_Key': 'County/State'})


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



# %%
# Creating a categorical column to use in the treemap to use colors for each state
codes = pd.DataFrame(df_all_trees['parent'].astype('category'))
codes["parent"] = codes["parent"].cat.codes
df_all_trees['codes'] = codes['parent']


# %%
import datetime
today = datetime.date.today()
yesterday = today - datetime.timedelta(days=1)

fig = make_subplots(1, 1, specs=[[{"type": "domain"}]])

fig.add_trace(go.Treemap(
    labels=df_all_trees['id'],
    parents=df_all_trees['parent'],
    values=df_all_trees['value'],
    branchvalues='total',
    marker=dict(
        colors=df_all_trees['codes'],
        colorscale='matter',
        #cmid=0.5
        ),
    hovertemplate='<b>%{label} </b> <br> Confirmed: %{value:,.2s}<br> %{percentParent:,.2%} of total<extra></extra>',
    texttemplate='<b>%{label} </b> <br> Confirmed: %{value:,.2s} <br> %{percentParent:,.2%} of total<br>',
    maxdepth=3,
    meta=df_all_trees['codes']
    ), 1, 1)

fig.update_layout(
    title='Cumulative confirmed cases per state and county as percentage of total in the US <br> Updated: ' + str(yesterday),
    #title='Cumulative confirmed COVID19 cases per state and county <br> as percentage of total in the US <br> Mar 16, 2020',
    title_x=0.5,
    #font=dict(size=9),
    #width=600,
    #height=800,
    hoverlabel=dict(
            bgcolor="white",
            font_size=16,
            font_color="#595959",
            font_family="Arial",
            bordercolor='#595959'
            ),
    )
fig.show()

import plotly.io as pio
pio.write_html(fig, file='Index.html', auto_open=True)

# import os

# if not os.path.exists("images"):
#     os.mkdir("images")

# fig.write_image("images/03-16-2020.svg")

# %%
