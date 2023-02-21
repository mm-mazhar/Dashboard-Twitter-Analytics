# # -*- coding: utf-8 -*-
"""
Created on Tuesday May 24 2022
@author: Mazhar
Description: This file is part of the Twitter Analytics Dashboard.
"""

import dash
import dash_bootstrap_components as dbc
from dash import html
from dash.dependencies import Output, Input
import configparser
import tweepy
from flask import Flask

# read configs
apiKeysFile  = "./config.ini"
config = configparser.ConfigParser(interpolation = None)
config.read(apiKeysFile)
bearer_token = config['twitter']['bearer_token']
consumer_key = config['twitter']['api_key']
consumer_secret = config['twitter']['api_key_secret']
access_token = config['twitter']['access_token']
access_token_secret = config['twitter']['access_token_secret']





auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)
client = tweepy.Client(bearer_token)
print("Twitter API connected")


app = dash.Dash(__name__, suppress_callback_exceptions = True, external_stylesheets = [dbc.themes.LUX], 
                meta_tags = [{'name': 'viewport', 'content': 'width = device-width, initial-scale = 1.0'}]
                )
app.title = "Twitter Analytics Dash App"
server = app.server

# The way gunicorn works import following to avoid circular imports
import appTabs

