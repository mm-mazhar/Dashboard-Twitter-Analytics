# -*- coding: utf-8 -*-
"""
Created on Tuesday May 24 2022
@author: Mazhar
Description: This file gets Twitter Users data.
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

#function so you can insert url link inside Dash DataTable
def f(row):
    return "[{0}]({0})".format(row["URL"])

# ============layout of tab 'Get Users' =============================
getUsersData_layout = dbc.Container([
    
    dbc.Row([
        
        # Input User ID
        dbc.Col([
            html.Label("Enter User ID:", className = "mt-2"),
            dcc.Input(
                    id = "user-id",
                    type = "text",
                    placeholder = "2244994945",
                    value = "2244994945",
                    style = {"width": "100%", "margin-top": "5px", "border-radius": "5px"},
                        ),
        ], width = 4,), 
        
        # Submit button for User ID
        dbc.Col([
            html.Button(
            id = "hit-button-user-id",
            children = "Submit",
            style = {"background-color": "#238fe2",
                        "color": "#5FFFFF", 
                        "border-color": "#238fe2",
                        "width": "100%",
                        "margin-top": "37px",
                        "border-radius": "5px",
                        },)
        ], width = 2,)
    ], className = "mt-4"),
    
    # Notification
        dbc.Row(
            [
            dbc.Col(
                [
                html.P(
                    id = "notification-GetUsersData",
                    children = "",
                    style = {"textAlign": "center", 'font-size': '16px', 'color': '#2f91e0', 'font-weight': 'bold'},
                )
                ],
                    width = 12,
                )
            ], 
            className = "mt-3",
        ),
    
    # Data Table
    dbc.Row([
        dbc.Col([
            html.Div(id = 'table-div-user', children = "")
        ], width = 12),
    ], className = "mt-4",),
    
    # Interval for updating trends (not shown in tab, works in background)
    #dcc.Interval(id = 'timer', interval = 1000*300, n_intervals = 0)
])


#================== Pull User Info and Create Table =========================
@app.callback(
    Output(component_id = "notification-GetUsersData", component_property = "children"),
    Output(component_id = "table-div-user", component_property = "children"),
    #Input(component_id = "timer", component_property = "n_intervals"),
    Input(component_id = "hit-button-user-id", component_property = "n_clicks"),
    State(component_id = "user-id", component_property = "value"),
    
)
#def displayTrends(timer, n_clicks, userID): # timer is used
def displayUser(n_clicks, userID): # timer is not used
    try:
        userID = userID.strip()
        id, name, username, location, description, created_at = [], [], [], [], [], []
        followers_count, following_count, tweet_count, listed_count = [], [], [], []
        url = []
        # profile_image_url = []
        # verified, withheld = [], [],
        # pinned_tweet_id, protected = [], []
        
        # =====get user data=====
        try:
            response = client.get_users(ids = userID, user_fields = 'id,name,username,created_at,description,location,pinned_tweet_id,profile_image_url,protected,public_metrics,url,verified,withheld')
        #response = client.get_users(ids = user_ids)
        except Exception as e:
            print("Error : " + str(e))
        
        for user in response.data:
            id.append(user.id)
            name.append(user.name)
            username.append(user.username)
            location.append(user.location)
            description.append(user.description)
            created_at.append(user.created_at)
            followers_count.append(user.public_metrics['followers_count'])
            following_count.append(user.public_metrics['following_count'])
            tweet_count.append(user.public_metrics['tweet_count'])
            listed_count.append(user.public_metrics['listed_count'])
            url.append(user.url)
            # profile_image_url.append(user.profile_image_url)
            # verified.append(user.verified)
            # withheld.append(user.withheld)
            # pinned_tweet_id.append(user.pinned_tweet_id)
            # protected.append(user.protected)
            
            _dict = {"ID": id,
                    "Name": name,
                    "Username": username,
                    "Location": location,
                    "Description": description,
                    "Created At": created_at,
                    "Followers Count": followers_count,
                    "Following Count": following_count,
                    "Tweet Count": tweet_count,
                    "Listed Count": listed_count,
                    "URL": url,
                    #  "Profile Image URL": profile_image_url,
                    #  "Verified": verified,
                    #  "Withheld": withheld,
                    #  "Pinned Tweet ID": pinned_tweet_id,
                    #  "Protected": protected,
                    }
            
            df = pd.DataFrame(_dict)
            
            #apply function so you can insert url link inside Dash DataTable
            df["URL"] = df.apply(f, axis = 1)
            
            # print(user.id, user.name, user.username, user.profile_image_url, user.location, user.description, \
            # user.created_at, user.verified, user.pinned_tweet_id, user.protected, \
            # user.public_metrics['followers_count'], user.public_metrics['following_count'], \
            # user.public_metrics['tweet_count'], user.public_metrics['listed_count'], \
            # user.url, user.verified, user.withheld)
            
            ###################################### Table ############################################
            dashTable = dash_table.DataTable(
            id = 'datatable-user',
            columns = [
                {"name": i, "id": i}
                if i == "ID" or i == "Name"
                else {"name": i, "id": i, 'type': 'text', "presentation":"markdown"}
                for i in df.columns
            ],
            data = df.to_dict('records'),
            markdown_options = dict(html = True, link_target = '_blank'),
            filter_action="native",
            page_action = 'native',
            page_size = 5,
            
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
        return "", dashTable
    except Exception as e:
        #print(e)
        return "Something went wrong Check 'User ID'", "  No Table: Error"
    
   