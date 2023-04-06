import os
import asyncio
import tweepy.asynchronous
from config import *
from datetime import datetime, date, timedelta
import random
from main import getUserID

# To set your environment variables in your terminal run the following line:
os.environ['BEARER_TOKEN'] = BEARER_TOKEN
bearer_token = os.environ.get('BEARER_TOKEN')

if oauth2_access_token == "":
    print("(i) - Getting new access token...")
    get_access_token()

# Configuring async tweepy client
AsyncClient = tweepy.asynchronous.AsyncClient(bearer_token=bearer_token, consumer_key=consumer_key,
                                              consumer_secret=consumer_secret,
                                              access_token=access_token, access_token_secret=access_token_secret,
                                              return_type=dict, wait_on_rate_limit=True)
oauth2AsyncClient = tweepy.asynchronous.AsyncClient(bearer_token=oauth2_access_token, consumer_key=consumer_key,
                                              consumer_secret=consumer_secret,
                                              access_token=access_token, access_token_secret=access_token_secret,
                                              return_type=dict, wait_on_rate_limit=True)

async def check_inactive(followed_users, period):
    """
    Checks for each followed account if it is inactive depending on the period
    :param followed_users: The array of followed accounts
    :param period: maximum number of days of the last tweet

    This function uses the Twitter API following endpoint:
    - https://api.twitter.com/2/users/:id/tweets
        > This endpoint is limited to 300 requests each 15 mins
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
            # Gets user ID for each account
            userId = getUserID(username)[0]

            recent_tweets = []
            if not "data" in recent_tweets:

                # Obtains the last 5 tweets from each followed account
                recent_tweets = await AsyncClient.get_users_tweets(id=userId, max_results=5, tweet_fields="created_at",
                                                       user_fields="username")
                # Skips private accounts
                if "errors" in recent_tweets:
                    if recent_tweets["errors"][0]["detail"] == f'Sorry, you are not authorized to see the user whith id: [{userId}].':
                        continue

                # Obtains the date of the last tweet
                if "data" in recent_tweets:
                    created_at_iso = recent_tweets["data"][0]["created_at"]
                    created_at = datetime.fromisoformat(created_at_iso[:-1])
                else:
                    pass

                # Checks if an account is inactive (tweet date is older than limit_date)
                if created_at < limit_date:
                    inactives.append(userId)

        except tweepy.errors.TweepyException:
            if tweepy.errors.TooManyRequests:
                print("(!) - Twitter API rate limit has reached. Should wait 15 mins to rerun")
                break
        except Exception as e:
            print(f"(!) ERROR: {e}")
            break

    n_inactives = len(inactives)
    if n_inactives == 0:
        print("(i) - No inactive accounts have been found for the introduced period")
    else:
        print(f"(i) - {n_inactives} inactive accounts have been found. Do you want unfollow them? (y/n)")
        response = input().lower()

        while response not in ["y", "n"]:
            print("(!) - Invalid input. Valid answers are 'y' (yes) or 'n' (no)")
            response = input().lower()

        if response == "y":
            await unfollow_user(inactives)
        elif response == "n":
            print("(i) - Closing program...")

async def unfollow_user(inactives):
    """
    Executes the unfollow action for each account in the array of inactive accounts
    :param inactives: The array of inactive accounts

    This function uses the Twitter API unfollow endpoint:
    - https://api.twitter.com/2/users/:source_user_id/following/:target_user_id
        > This endpoint is limited to 50 requests each 15 mins
    """
    unfollowed = []

    for user in inactives:
        try:
            await asyncio.shield(oauth2AsyncClient.unfollow_user(user))
            print(f"(i) - Unfollowing account with ID: {user}")
            unfollowed.append(user)
        except tweepy.errors.TweepyException:
            if tweepy.errors.TooManyRequests:
                print("(!) - Twitter API rate limit has reached. Should wait 15 mins to rerun")
                break
        except Exception as e:
            print(f"(!) - ERROR: {e}")
            break

    n_unfollows = len(unfollowed)
    if n_unfollows == 0:
        print("(i) - No accounts have been unfollowed")
    else:
        print(f"(i) - {n_unfollows} inactive accounts have been unfollowed.")
