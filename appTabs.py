# -*- coding: utf-8 -*-
"""
Created on Tuesday May 24 2022
@author: Mazhar
Description: This file connects to twitter, displays Tabs of the app and connects to other files.
This file is to run when the app is run.
"""
import dash_bootstrap_components as dbc
from dash import html
from dash.dependencies import Output, Input
from app import app, server
# Connect to the layout and callbacks of each tab
from appTweetsSearch import tweetsSearch_layout
from appTrends import trends_layout
#from other import other_layout
from getUsersInfo import getUsersData_layout
from getUsersTweet import getUsersTweet_layout

#================== App's Tabs ===========================================================================================
app_tabs = html.Div(
    [
        dbc.Tabs(
            [   
                dbc.Tab(label = "Trends", tab_id = "tab-trends", labelClassName = "text-success font-weight-bold", activeLabelClassName = "text-danger"),
                dbc.Tab(label = "Recent Search", tab_id = "tab-tweetsSearch", labelClassName = "text-success font-weight-bold", activeLabelClassName = "text-danger"),
                dbc.Tab(label = "Get Users Info", tab_id = "tab-users", labelClassName = "text-success font-weight-bold", activeLabelClassName = "text-danger"),
                dbc.Tab(label = "Get Users Tweet", tab_id = "tab-users-tweet", labelClassName = "text-success font-weight-bold", activeLabelClassName = "text-danger"),
            ],
            id = "tabs",
            active_tab = "tab-trends",
        ),
    ], className = "mt-3"
)

app.layout = dbc.Container([
    dbc.Row(dbc.Col(html.H1("LIVE Twitter Analytics Dashboard",
                            style = {"textAlign": "center"}), className = "mt-5", width = 12)),
    html.Hr(),
    dbc.Row(dbc.Col(app_tabs, width = 12), className = "mb-3"),
    html.Div(id = 'content', children = [])

])

@app.callback(
    Output("content", "children"),
    [Input("tabs", "active_tab")]
) 
def switch_tab(tab_chosen):
    if tab_chosen == "tab-trends":
        return trends_layout
    elif tab_chosen == "tab-tweetsSearch":
        return tweetsSearch_layout
    elif tab_chosen == "tab-users":
        return getUsersData_layout
    elif tab_chosen == "tab-users-tweet":
        return getUsersTweet_layout
        
    return html.P("This shouldn't be displayed for now...")



if __name__ == '__main__':
    app.run_server(debug = True, port=8050)
    