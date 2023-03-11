import os
import json
import tweepy.asynchronous
from config import *
from globals import initialize

# To set your environment variables in your terminal run the following line:
os.environ['BEARER_TOKEN'] = BEARER_TOKEN
bearer_token = os.environ.get('BEARER_TOKEN')

# Configuring async tweepy client
AsyncClient = tweepy.asynchronous.AsyncClient(bearer_token=bearer_token, consumer_key=consumer_key,
                                              consumer_secret=consumer_secret,
                                              access_token=access_token, access_token_secret=access_token_secret,
                                              return_type=dict)


# Contains all the followed accounts obtained in the previous step
def check_inactive():
    print()
