# -*- coding: utf-8 -*-
"""
Created on Tuesday May 24 2022
@author: Mazhar
Description: This file gets tweets of Users, displays word clound and count of words bar graph.
"""
from hashlib import new
import plotly.express as px
import dash_bootstrap_components as dbc
from dash import dash_table
from dash import html
from dash import dcc
from dash.dependencies import Output, Input, State
import pandas as pd
from app import app, api, client
import json
import re
from collections import Counter
from datetime import datetime
import nltk
from wordcloud import WordCloud
nltk.download('stopwords') # only downlaod once
# Resource: https://python-twitter.readthedocs.io/en/latest/twitter.html

#Create stopword list for wordcloud analysis later:
stopwords = nltk.corpus.stopwords.words('english')
stopwords = set(stopwords)
stopwords.update([
    "Are", "In", "Not", "We", "Also", 
    ])

#function so you can insert url link inside Dash DataTable
def f(row):
    return "[{0}]({0})".format(row["URL"])

# Clean Text Function
def cleanText(text):
    
    text = re.sub(r'@', '', text)                                           # remove @
    text = re.sub(r'@[A-Za-z0-9]+', '', text)                               # remove @mentions
    text = re.sub(r'https?:\/\/S+', '', text)                               # remove URLs
    text = re.sub(r'^https?:\/\/.*[\r\n]*', '', text, flags=re.MULTILINE)   # remove URLs
    text = re.sub(r'http[^A-Za-z0-9]+', ' ', text)                          # remove non-alphanumeric
    text = re.sub(r'RT[\s]+', '', text)                                     # remove RT
    text = re.sub(r'#', '', text)                                           # remove '#'
    text  = re.sub(r'[^\w\s]', '', text)                                    # remove punctuation
    # remove emojis
    emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                           "]+", flags=re.UNICODE)
    text = emoji_pattern.sub(r'', text)                                     # remove emoji
    
    return text


# Remove Stopwords Function
def remove_stopwords(text):
    """Remove stop words from list of tokenized words"""
    newText = []
    for word in text:
        # if word not in nltk.corpus.stopwords.words('english'):
        if word not in stopwords:
            newText.append(word)
    return newText


# ============layout of tab 'Get Users Tweet' =============================
getUsersTweet_layout = dbc.Container([
    
    # Input User ID and Submit button
    dbc.Row([
        # Input User ID
        dbc.Col([
            html.Label("Enter User ID:", className = "mt-2"),
            dcc.Input(
                    id = "usertweet",
                    type = "text",
                    placeholder = "2244994945",
                    value = "2244994945",
                    style = {"width": "100%", "margin-top": "5px", "border-radius": "5px"},
                        ),
        ], width = 4,), 
        
        # Submit Button for User ID
        dbc.Col([
            html.Button(
            id = "hit-button-usertweet",
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
                    id = "notification-UsersTweet",
                    children = "",
                    style = {"textAlign": "center", 'font-size': '16px', 'color': '#2f91e0', 'font-weight': 'bold'},
                )
                ],
                    width = 12,
                )
            ], 
            className = "mt-4",
        ),
    
    # Word Cloud and Word Count Bar Graph
    dbc.Row([
        dbc.Col([
            html.Div(id = 'figure-div', children = "")
        ], width = 6),
        
        dbc.Col([
            #html.Div(id = 'figure-div2', children = ""),
            dbc.Col([dcc.Graph(id = "barChart-wordCount", figure = {})]),
        ], width = 6),
        ], className = "mt-4"),
    
    # Data Table
    dbc.Row([
        dbc.Col([
            html.Div(id = 'table-div-usertweet', children = "")
        ], width = 12),
    ], className = "mt-4",),
    
    
    # Interval for updating trends (not shown in tab, works in background)
    #dcc.Interval(id = 'timer', interval = 1000*300, n_intervals = 0)
])


#======================= Word Cloud and Word Count Bar Graph ==============================
@app.callback(
    Output(component_id = "notification-UsersTweet", component_property = "children"),
    Output(component_id = "figure-div", component_property = "children"),
    Output(component_id = "barChart-wordCount", component_property = "figure"),
    #Input(component_id = "timer", component_property = "n_intervals"),
    Input(component_id = "hit-button-usertweet", component_property = "n_clicks"),
    State(component_id = "usertweet", component_property = "value"),
)
def displayUserTweet(n_clicks, user_id): # timer is not used
    
    try:
        
        response = client.get_users_tweets(user_id, max_results = 100)

        # By default, only the ID and text fields of each Tweet will be returned
        # for tweet in response.data:
        #     print(tweet.id)
        #     print(tweet.text)

        # join all tweet text into one string
        alltweets = " ".join(tweet.text for tweet in response.data)

        #=============== Word Cloud ==================
        # generate wordcloud from all tweets
        my_wordcloud = WordCloud(
            stopwords = stopwords,
            background_color = 'white',
            height = 275
        ).generate(alltweets)

        # visualize wordcloud inside plotly figure
        fig = px.imshow(my_wordcloud, template = 'ggplot2')
        fig.update_layout(margin = dict(l = 20, r = 20, t = 30, b = 20))
        fig.update_xaxes(visible = False)
        fig.update_yaxes(visible = False)
        
        #============== Word Count Bar Graph ============
        
        cleanTweets = cleanText(alltweets)
        tweetsList = remove_stopwords(cleanTweets.split())
        tweetsList = sorted(tweetsList)
        #tweetsList = cleanTweets.split()
        tweetsDict = Counter(tweetsList)
        x = list(tweetsDict.keys())
        y = list(tweetsDict.values())
        
        
        barChartWordCount = px.bar(x = x, 
                                y = y,
                                color = x,
                                labels = {'x': 'Words', 'y': 'Count'},
                                title = f"Word Count of All Tweets of User: {user_id}",
                        )
        
        barChartWordCount.update_layout({
            "plot_bgcolor": "#000000",
            "paper_bgcolor": "#000000",
            "font": {"color": "#FFFFFF"},
            })
        return "Word Cloud and Word Count", dcc.Graph(figure = fig), barChartWordCount
    except Exception as e:
        #print(e)
        return "Something went wrong Check 'User ID'", "Error", "Error"
            

#================ Pull Tweets by User and Create Table ================================
@app.callback(
    #Output(component_id = "notification-UsersTweet", component_property = "children"),
    Output(component_id = "table-div-usertweet", component_property = "children"),
    #Input(component_id = "timer", component_property = "n_intervals"),
    Input(component_id = "hit-button-usertweet", component_property = "n_clicks"),
    State(component_id = "usertweet", component_property = "value"),
    
)
#def displayTrends(timer, n_clicks, country): # timer is used
def displayUserTweet(n_clicks, user_id): # timer is not used
    try:
        column_names = ["tweet_id", "tweet_text"]
        df = pd.DataFrame(columns = column_names)
        user_id = user_id.strip()

        # By default, the 10 most recent Tweets will be returned
        # You can retrieve up to 100 Tweets by specifying max_results
        response = client.get_users_tweets(user_id, max_results = 100)

        # By default, only the ID and text fields of each Tweet will be returned
        df["tweet_id"] = [tweet.id for tweet in response.data] 
        df["tweet_text"] = [tweet.text for tweet in response.data]
        
        #========= Table ==================
        dashTable = dash_table.DataTable(
        id = 'datatable-userTweet',
        columns = [
            {"name": i, "id": i}
            if i == "tweet_id" or i == "tweet_text"
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
    
