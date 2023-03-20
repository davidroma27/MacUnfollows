import os
import tweepy.asynchronous
from config import *
from datetime import datetime, date, timedelta
import random
from main import getUserID

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
    today = datetime.today()
    created_at = ""
    selected_users = []

    # Calculates the limit date
    limit_date = today - timedelta(days=period)

    for x in range(len(followed_users)):
        # Select a random account to check without choose the same account twice
        user = random.choice([u for u in followed_users if u not in selected_users])
        selected_users.append(user)
        username = user["username"]

        try:
            #Gets user ID for each account
            userId = getUserID(username)[0]

            recent_tweets = []
            if not "data" in recent_tweets:

                # Obtains the last 5 tweets from each followed account
                recent_tweets = await AsyncClient.get_users_tweets(id=userId, max_results=5, tweet_fields="created_at",
                                                       user_fields="username")
                if "errors" in recent_tweets:
                    if recent_tweets["errors"][0]["title"] == 'Authorization Error':
                        continue

                # Obtains the date of the last tweet
                if "data" in recent_tweets:
                    created_at_iso = recent_tweets["data"][0]["created_at"]
                    created_at = datetime.fromisoformat(created_at_iso[:-1])
                else:
                    pass

                # Checks if an account is inactive (tweet date is older than limit_date)
                if created_at < limit_date:
                    inactives.append(username)

        except tweepy.errors.TweepyException:
            if tweepy.errors.TooManyRequests:
                print("(i) - Twitter API rate limit has reached. Should wait 15 mins to rerun")
                break
        except Exception as e:
            print(f"Error: {e}")
            break

    n_inactives = len(inactives)
    if n_inactives == 0:
        print("(i) - No inactive accounts have been found for the introduced period")
    else:
        print(f"(i) - {n_inactives} inactive accounts have been found. Do you want unfollow them? (y/n)")

    print(inactives)
    return inactives
