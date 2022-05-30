# -*- coding: utf-8 -*-
"""
Created on Tuesday May 24 2022
@author: Mazhar
Description: This file is process Twitter Trends.
"""
import plotly.express as px
import dash_bootstrap_components as dbc
from dash import dash_table
from dash import html
from dash import dcc
from dash.dependencies import Output, Input, State
import pandas as pd
from app import app, api, client
import json
from datetime import datetime


### Creating Generator Object: Reading JSON file, remove invalid parentids, \
### list of Country and ParentID, remove duplicates, yield list of woeid, Country and ParentID
def woidsGenerator(woeidsJSONFile, locationTrends):
    _list = []
    lstCountryParentid = []
    # 1) Reading JSON file
    with open(woeidsJSONFile) as file:
        data = json.load(file)
    # 2) iterate over and remove invalid parentids
    for i in range(len(data)):
        if data[i]['parentid'] != 1:
            temp = {"City": str(data[i]['name']), "Country": str(data[i]['country']), "Parentid": str(data[i]['parentid']), "Woeid": str(data[i]['woeid'])}
        _list.append(temp)
    # 3) list of Country and ParentID
    for i in range(len(_list)):
        temp = {"Country": str(_list[i]['Country']), "Parentid": str(_list[i]['Parentid'])}
        lstCountryParentid.append(temp)
    # 4) using list comprehension to remove duplicates 
    lstCountryParentid = [i for n, i in enumerate(lstCountryParentid) if i not in lstCountryParentid[n + 1:]]
    for i in range(len(lstCountryParentid)):
        if lstCountryParentid[i]['Country'] == locationTrends:
            woeid = lstCountryParentid[i]['Parentid']
    yield woeid, lstCountryParentid


#function so you can insert url link inside Dash DataTable
def f(row):
    return "[{0}]({0})".format(row["URL"])


locationTrends = "United States"
tupleObj = woidsGenerator("woeids.json", locationTrends)
woeid, lstCountryParentid = next(tupleObj)
#print("WOEID: ", woeid)
#print("ParentID: ", lstCountryParentid)
listCountry = [i["Country"] for i in lstCountryParentid]
#print("List of Countries: ", listCountry)
#print(sys.getsizeof(tupleObj))


#========================== layout of tab 'Trends' =============================
trends_layout = dbc.Container([
    
    # Title Row
    dbc.Row([
        dbc.Col([
            html.H3("Most trending topics in countries & Word Cloud Analysis of tweets ")
        ], width = 12)
    ], className = "mt-4"),
    
    dbc.Row([
        
        # Dropdown menu for selecting country
        dbc.Col([
            html.Label("Select a country to see on going trends"),
            dcc.Dropdown(
                id = "trends-country-dropdown",
                multi = False,
                value = "Pakistan",
                options = listCountry,
                searchable = True,
                clearable = False,),
        ], width = 4,), 
        
        # Submit button for selecting country
        dbc.Col([
            html.Button(
            id = "hit-button",
            children = "Submit",
            style = {"background-color": "#238fe2",
                        "color": "#5FFFFF", 
                        "border-color": "#238fe2",
                        "width": "100%",
                        "margin-top": "25px",
                        "border-radius": "5px",
                        },)
        ], width = 2,)
    ], className = "mt-4"),
    
    # Notification 
    dbc.Row([
            dbc.Col(
                [
                    html.P(
                        id = "notification-trends",
                        children = "",
                        style = {"textAlign": "center", 'font-size': '16px', 'color': '#2f91e0', 'font-weight': 'bold'},
                    )
                ], width = 12,
            )], className = "mt-4",
        ),
    
    # Dash table for displaying trends
    dbc.Row([
        dbc.Col([
            html.Div(id = 'table-div', children = "")
        ], width = 12),
        
        # dbc.Col([
        #     html.Div(id = 'figure-div', children = "")
        # ], width = 6),
    ], className = "mt-4",),
    
    # Interval for updating trends (not shown in tab, works in background)
    #dcc.Interval(id = 'timer', interval = 1000*300, n_intervals = 0)
])


# pull trending tweets and create the table ******************************
@app.callback(
    Output(component_id = "notification-trends", component_property = "children"),
    Output(component_id = "table-div", component_property = "children"),
    #Input(component_id = "timer", component_property = "n_intervals"),
    Input(component_id = "hit-button", component_property = "n_clicks"),
    State(component_id = "trends-country-dropdown", component_property = "value"),
    
)
#def displayTrends(timer, n_clicks, country): # timer is used
def displayTrends(n_clicks, country): # timer is not used
    trnd_name, trnd_vol, trnd_url = [], [], []
    date = datetime.now().date()
    locationTrends = country
    tupleObj = woidsGenerator("woeids.json", locationTrends)
    woeid, lstCountryParentid = next(tupleObj)
    trendsResult = api.get_place_trends(woeid)
    i = 1
    # print("WOEID: ".format(woeid))
    try:
        for trend in trendsResult[0]['trends']:
            trnd_name.append(trend['name'])
            trnd_vol.append(trend['tweet_volume'])
            trnd_url.append(trend['url'])
            i += 1
        
        _dict = {'Trend Name': trnd_name, 'Tweet Volume': trnd_vol, 'URL': trnd_url}
        df = pd.DataFrame(_dict)
        #apply function so you can insert url link inside Dash DataTable
        df["URL"] = df.apply(f, axis = 1)
        #print(df.head())
    except Exception as e:
        print("Error: {}".format(e))
    
    message = f"Trends today {date} in {locationTrends}"
    
    #========= Table ==================
    dashTable = dash_table.DataTable(
        id = 'datatable-trends',
        columns = [
            {"name": i, "id": i}
            if i == "Trend Name" or i == "Tweet Volume"
            else {"name": i, "id": i, 'type': 'text', "presentation":"markdown"}
            for i in df.columns
        ],
        data = df.to_dict('records'),
        markdown_options = dict(html = True, link_target = '_blank'),
        filter_action="native",
        page_action = 'native',
        page_size = 10,
        
        # Data Table Styling
        style_cell_conditional = [
        {
            'if': {'column_id': c},
            'textAlign': 'left'
        } for c in ['Trend Name', 'Trend Volume']
        ],
        style_data = {
            'color': 'black',
            'backgroundColor': 'white'
        },
        style_data_conditional = [ 
            {
                'if': {'row_index': 'even'},
                'backgroundColor': 'rgb(220, 220, 220)',
            }
        ],
        
        style_header = {
        'backgroundColor': '#2f91e0',
        'color': 'black',
        'fontWeight': 'bold',
        'textAlign': 'left',
        'fontSize': '10px',
        },
        
        style_cell = {
            'textAlign': 'left',
            'whiteSpace': 'normal',
            'height': 'auto',
            'overflow': 'hidden',
            'minWidth': '50px', 'width': '80px', 'maxWidth': '120px',
            'fontSize': '9px',
        },
    )
    
    return message, dashTable



