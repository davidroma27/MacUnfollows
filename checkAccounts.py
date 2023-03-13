import os
import tweepy.asynchronous
from config import *
from datetime import datetime, date, timedelta

# To set your environment variables in your terminal run the following line:
os.environ['BEARER_TOKEN'] = BEARER_TOKEN
bearer_token = os.environ.get('BEARER_TOKEN')

# Configuring async tweepy client
AsyncClient = tweepy.asynchronous.AsyncClient(bearer_token=bearer_token, consumer_key=consumer_key,
                                              consumer_secret=consumer_secret,
                                              access_token=access_token, access_token_secret=access_token_secret,
                                              return_type=dict, wait_on_rate_limit=True)

async def check_inactive(followed_users, period) -> list:
    """
    Checks for each followed account if it is inactive depending on the period
    :param followed_users: The array of followed accounts
    :param period: maximum number of days of the last tweet
    """
    period = int(period)
    inactives = []
    today = date.today()
    req = 0

    for user in followed_users:
        username = user["username"]
        try:
            # Obtains the last 10 tweets from each followed account
            recent_tweets = await AsyncClient.search_recent_tweets(query=username, max_results=10, tweet_fields="created_at",
                                                   user_fields="username")
        except Exception as e:
            print(f"Error: {e}")
            break

        req += 1
        if req == 400:
            print(" ! - Limit has reached")

        # Obtains the date of the last tweet
        created_at_iso = recent_tweets["data"][0]["created_at"]
        created_at = datetime.fromisoformat(created_at_iso)

        # Calculates the limit date
        limit_date = today - timedelta(days=period)

        # Checks if an account is inactive (tweet date is older than limit_date)
        if created_at < limit_date:
            inactives.append(username)

        if len(inactives) == 0:
            print("(i) - No inactive accounts have been found for the introduced period")
        else:
            n_inactives = len(inactives)
            print(f"(i) - {n_inactives} inactive accounts have been found. Do you want unfollow them? (y/n)")
        print(inactives)

    return inactives
