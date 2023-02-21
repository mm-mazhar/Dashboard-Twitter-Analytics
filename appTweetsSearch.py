# -*- coding: utf-8 -*-
"""
Created on Tuesday May 24 2022
@author: Mazhar
Description: This file displays Analytics of Twitter Search Results on inputted Keywords.
"""

import plotly.express as px
import dash_bootstrap_components as dbc
from dash import html
from dash import dcc
from dash import dash_table
from dash.dependencies import Output, Input, State
import pandas as pd
from app import app, client
import re
import time

# Clean Text Function
def cleanText(text):
    
    text = re.sub(r'@', '', text) # remove @
    #text = re.sub(r'@[A-Za-z0-9]+', '', text) # remove @mentions
    text = re.sub(r'https?:\/\/S+', '', text) # remove URLs
    text = re.sub(r'RT[\s]+', '', text) # remove RT
    text = re.sub(r'#', '', text)   # remove '#'
    
    return text

# ============layout of tab 'Recent Search' =============================
tweetsSearch_layout = html.Div(
    [   
        # Note Row
        dbc.Row([
            html.P("Enter Keyword to search for in the search bar. Please note that Twitter API v2 (elevated access) only gives maximum of 100 results per query. \
                   Also retweets are excluded and tweets in 'English Language' are taken into account.", className = "text-info"),
            ], className = "mt-2"),
        
        # Number of Results, Search Bar
        dbc.Row(
            [
                # Number of Results
                dbc.Col(
                    [
                        html.Label("Number of results to return"),
                        dcc.Dropdown(
                            id = "countSearchResults",
                            multi = False,
                            value = 100,
                            options = [
                                {"label": "10", "value": 10},
                                {"label": "50", "value": 50},
                                {"label": "100", "value": 100},
                            ],
                            clearable = False,
                        ),
                    ],
                    width = 3,
                ),
                
                # Search Bar
                dbc.Col(
                    [
                        html.Label("Search"),
                        dcc.Input(
                            id = "input-handle",
                            type = "text",
                            placeholder = "Enter Search Term",
                            value = "Python",
                            style = {"width": "100%", "margin-top": "5px", "border-radius": "5px"},
                        ),
                    ],
                    width = 3,
                ),
            ],
            className = "mt-2",
        ),
        
        # Submit Button
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.Button(
                            id = "hit-button",
                            children = "Submit",
                            style = {"background-color": "#238fe2", "color": "#5FFFFF", "border-color": "#238fe2"},
                        )
                    ],
                    width = 2,
                )
            ],
            className = "mt-2",
        ),
        
        # Notification
        dbc.Row(
            [
            dbc.Col(
                [
                html.P(
                    id = "notification",
                    children = "",
                    style = {"textAlign": "center", 'font-size': '16px', 'color': '#2f91e0', 'font-weight': 'bold'},
                )
                ],
                    width = 12,
                )
            ], 
            className = "mt-3",
        ),
        
        # Graphs
        dbc.Row(
            [
                dbc.Col([dcc.Graph(id = "barChart", figure = {})], width = 6),
                dbc.Col([dcc.Graph(id = "barChart2", figure = {})], width = 6),
            ],
            className = "mt-3",
        ),
        
        # Dash table for displaying trends
        dbc.Row([
            dbc.Col([
                html.Div(id = 'table-div-search', children = "")
            ], width = 12),
        ], className = "mt-4",),
    ]
)


# Pull Data from Twitter and Create Figures
@app.callback(
    Output(component_id = "notification", component_property = "children"),
    Output(component_id = "barChart", component_property = "figure"),
    Output(component_id = "barChart2", component_property = "figure"),
    Output(component_id = "table-div-search", component_property = "children"),
    Input(component_id = "hit-button", component_property = "n_clicks"),
    State(component_id = "countSearchResults", component_property = "value"),
    State(component_id = "input-handle", component_property = "value"),
)
def display_value(nclicks, num,  searchTerm):
    try:
        query = cleanText(searchTerm)
        #print(query)
        #print(type((query)))

        tweets = []
        response = client.search_recent_tweets(
                                        #query = 'COVID hoax -is:retweet lang:en',
                                        query = query + " " + "-is:retweet lang:en",
                                        user_fields = ['username', 'public_metrics', 'description', 'location'],
                                        tweet_fields = ['created_at', 'geo', 'public_metrics', 'text'],
                                        expansions = 'author_id',
                                        max_results = num)
        time.sleep(1)
        tweets.append(response)
            
        #print(tweets)
        # print(tweets[0].data[0])
        # print(tweets[0].includes['users'][2])
        # print(tweets[0].includes['users'][2].description)

        # print(response.meta)
        # tweets = response.data
        # # Each Tweet object has default ID and text fields
        # for tweet in tweets:
        #     print(tweet.id)
        #     print(tweet.text)

        result = []
        user_dict = {}
        # Loop through each response object
        for response in tweets:
            # Take all of the users, and put them into a dictionary of dictionaries with the info we want to keep
            for user in response.includes['users']:
                user_dict[user.id] = {'username': user.username, 
                                    'followers': user.public_metrics['followers_count'],
                                    'tweets': user.public_metrics['tweet_count'],
                                    'description': user.description,
                                    'location': user.location
                                    }
            for tweet in response.data:
                # For each tweet, find the author's information
                author_info = user_dict[tweet.author_id]
                # Put all of the information we want to keep in a single dictionary for each tweet
                result.append({'authorId': tweet.author_id, 
                            'User Name': author_info['username'],
                            'Author Followers': author_info['followers'],
                            'Author Tweets': author_info['tweets'],
                            'Author Description': author_info['description'],
                            'Author Location': author_info['location'],
                            'Text': tweet.text,
                            'Created At': tweet.created_at,
                            'Re Tweets': tweet.public_metrics['retweet_count'],
                            'Replies': tweet.public_metrics['reply_count'],
                            'Likes': tweet.public_metrics['like_count'],
                            'Quote Count': tweet.public_metrics['quote_count']
                            })

        # Change this list of dictionaries into a dataframe
        df = pd.DataFrame(result)
        #print(df.columns)
        #print(df[['User Name', 'Re Tweets', 'Replies', 'Likes', 'Quote Count']])

        mostFollowers = df['Author Followers'].max()
        mostFolwrsAccountName = df["User Name"][df['Author Followers'] == mostFollowers].values[0]
        
        message = f"The Twitter account that mentioned '{query}' for last 30 days is called '{mostFolwrsAccountName}' and it has the highest followers count: {mostFollowers} followers."

        #=================== Bar Charts ======================
        # Create 'most followers' bar chart
        
        barChart = px.bar(df, x = "User Name", y = "Author Followers", color = "User Name",
                        labels = {'User Name': 'User Name', 'Author Followers': 'Followers'},
                        title = f"Followers Count of Users who Mentions '{query}'"
                        )
        
        barChart.update_layout({
            "plot_bgcolor": "#000000",
            "paper_bgcolor": "#000000",
            "font": {"color": "#FFFFFF"},
            })
        
        barChart.update_yaxes(showgrid = False)
        barChart.update_yaxes(range = [0, df['Author Followers'].max() + 200 ])
        
        # Create 'most re Tweets' bar chart2
        barChart2 = px.bar(df, x = "User Name", y = "Re Tweets", color = "User Name", 
                        labels = {'User Name': 'User Name', 'Re Tweets': 'reTweets'},
                        title = f"Most Retweets by Users who Mentions '{query}'"
                        )
        
        barChart2.update_layout({
            "plot_bgcolor": "#000000",
            "paper_bgcolor": "#000000",
            "font": {"color": "#FFFFFF"},
            })
        
        barChart2.update_yaxes(showgrid = False)
        barChart2.update_yaxes(range = [0, df['Re Tweets'].max() + 2 ])
        
        
        #========= Table ==================
        dashTable = dash_table.DataTable(
            id = 'datatable-search',
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
            page_size = 3,
            
            # Data Table Styling
            style_cell_conditional = [
            {
                'if': {'column_id': c},
                'textAlign': 'left'
            } for c in ['Trend Name', 'Trend Volume']
            ],
            style_data = {
                'color': 'black',
                'backgroundColor': 'white', 
                
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
                'minWidth': '50px', 
                'width': '80px', 
                'maxWidth': '150px',
                'fontSize': '9px',
            },
        )
        return message, barChart, barChart2, dashTable
    except Exception as e:
        print(e)
        return "Something went wrong Check 'Search Term'", "Error", "Error", "Error"
    
    


