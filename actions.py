import os
import asyncio
import tweepy.asynchronous
from config import *
from datetime import datetime, date, timedelta
import random
import json

# To set your environment variables in your terminal run the following line:
os.environ['BEARER_TOKEN'] = BEARER_TOKEN
bearer_token = os.environ.get('BEARER_TOKEN')

# Get new access token the first time app executes
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


async def get_user_id(username) -> tuple:
    """
        Function to get User ID
    :param username: The Twitter username
    :return: user_id -> The ID of the user
    """
    global user_id
    global errors
    user_id = None
    errors = None

    user = await AsyncClient.get_user(username=username)
    try:
        if 'data' in user:
            user_id = user['data']['id']
            print(f"The {username}'s ID is : {user_id}")
        elif 'errors' in user:
            errors = user['errors']
    except Exception as e:
        print(f"Error: {e}")
    return user_id, errors

async def get_followed(user_id) -> tuple:
    """
    Returns a list of users the specified UserID is following
    :param user_id: The Twitter user ID
    :return: users - The list of followed users by the user
    """
    global users
    global errors
    users = []
    errors = None

    try:
        list = await AsyncClient.get_users_following(id=user_id, max_results=1000)

        # Check if list is returning data or returning errors
        if "data" in list:
            users = list['data']

            # check if exists "next_token" and get next page of users
            while 'next_token' in list['meta'].keys():
                next_token = list['meta']['next_token']
                list = await AsyncClient.get_users_following(id=user_id, max_results=1000, pagination_token=next_token)

                for e in list['data']:
                    users.append(e)

                # double check for the last page
                if 'next_token' in list['meta'].keys():
                    next_token = list['meta']['next_token']  # get next token
        elif 'errors' in list:
            errors = list['errors'][0]
    except Exception as e:
        print(f"(!) ERROR: {e}")

    return users, errors

async def check_inactive(followed_users, period):
    """
    Checks for each followed account if it is inactive depending on the period\n
    :param followed_users: The array of followed accounts
    :param period: maximum number of days of the last tweet

    This function uses the Twitter API following endpoint:\n
    - https://api.twitter.com/2/users/:id/tweets
    > This endpoint is limited to 300 requests each 15 mins
    """
    period = int(period)
    inactives = []
    today = datetime.today()
    created_at = ""
    selected_users = []
    inactive_json = {
        "period": period,
        "accounts": inactives
    }

    # Calculates the limit date
    limit_date = today - timedelta(days=period)

    for x in range(len(followed_users)):
        # Select a random account to check without choose the same account twice
        user = random.choice([u for u in followed_users if u not in selected_users])
        selected_users.append(user)
        username = user["username"]

        try:
            # Gets user ID for each account
            user_id = await get_user_id(username)

            recent_tweets = []
            if not "data" in recent_tweets:

                # Obtains the last 5 tweets from each followed account
                recent_tweets = await AsyncClient.get_users_tweets(id=user_id[0], max_results=5, tweet_fields="created_at",
                                                                   user_fields="username")
                # Skips private accounts
                if "errors" in recent_tweets:
                    if recent_tweets["errors"][0]["detail"] == f'Sorry, you are not authorized to see the user whith id: [{user_id[0]}].':
                        continue

                # Obtains the date of the last tweet
                if "data" in recent_tweets:
                    created_at_iso = recent_tweets["data"][0]["created_at"]
                    created_at = datetime.fromisoformat(created_at_iso[:-1])
                else:
                    pass

                # Checks if an account is inactive (last posted tweet date is older than limit_date)
                if created_at < limit_date:
                    inactives.append(int(user_id[0]))
                    # Save period and inactive accounts into json
                    with open("inactive_json.json", "w") as f:
                        json.dump(inactive_json, f, indent=4)
        except Exception as e:
            print(f"(!) ERROR: {e}")
            continue

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
            inactive_json = {
                "period": period,
                "accounts": inactives
            }
            await unfollow_user(inactive_json)
        elif response == "n":
            print("(i) - Closing program...")
            sys.exit(0)


async def unfollow_user(inactive_json):
    """
    Executes the unfollow action for each account in the array of inactive accounts
    :param inactives: The array of inactive accounts

    This function uses the Twitter API unfollow endpoint:\n
    - https://api.twitter.com/2/users/:source_user_id/following/:target_user_id
    > This endpoint is limited to 50 requests each 15 mins
    """
    unfollowed = []

    for user in inactive_json["accounts"]:
        try:
            await oauth2AsyncClient.unfollow_user(user)
            print(f"(i) - Unfollowing account with ID: {user}")
            unfollowed.append(user)
            # Remove unfollowed user from json file
            with open("inactive_json.json", "r") as output:
                data = json.load(output)
            data["accounts"].remove(user)
            with open("inactive_json.json", "w") as output:
                json.dump(data, output, indent=4)
        except Exception as e:
            print(f"(!) - ERROR: {e}")
            continue

    n_unfollows = len(unfollowed)
    if n_unfollows == 0:
        print("(i) - No accounts have been unfollowed")
    else:
        print(f"(i) - {n_unfollows} inactive accounts have been unfollowed.")
        sys.exit(0)


async def check_json(period):
    """
    Check if exists a json file with inactive accounts.
    If so, calls unfollow_user() with a list of that accounts
    """
    inactive_json = []
    res = ""
    try:
        if os.path.exists("inactive_json.json") and os.path.getsize("inactive_json.json") > 0:
            # Load the JSON data from the file into a Python dictionary
            with open("inactive_json.json", "r") as f:
                inactive_json = json.load(f)
            # Checks if the introduced period is the same that the stored in json
            if inactive_json["period"] == period:
                # Checks if inactive list has accounts
                if len(inactive_json["accounts"]) > 0:
                    print("(i) - You haven't unfollow some inactive acocunts yet. Do you want to unfollow them? (y/n)")
                    res = input().lower()

                    while res not in ["y", "n"]:
                        print("(!) - Invalid input. Valid answers are 'y' (yes) or 'n' (no)")
                        res = input().lower()

                    if res == "y":
                        await unfollow_user(inactive_json)
                    elif res == "n":
                        pass
            else:
                pass
    except Exception as e:
        print(f"(!) - ERROR: {e}")
        sys.exit(0)