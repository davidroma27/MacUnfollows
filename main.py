import requests
import os
import json

import tweepy

from config import *
from tweepy import OAuth1UserHandler

# To set your environment variables in your terminal run the following line:
os.environ['BEARER_TOKEN'] = BEARER_TOKEN
bearer_token = os.environ.get('BEARER_TOKEN')

# Configuring tweepy client
client = tweepy.Client(bearer_token=bearer_token, consumer_key=consumer_key, consumer_secret=consumer_secret,
                       access_token=access_token, access_token_secret=access_token_secret, return_type=dict)


def getUserID(username) -> int:
    """
        Function to get User ID
    :param username: The Twitter username
    :return: user_id -> The ID of the user
    """
    user = client.get_user(username=username)
    print(user)
    if user['data']:
        user_id = user['data']['id']
        print(f"The {username}'s ID is : {user_id}")
        return user_id
    elif user['errors']:
        # print("The username entered does not exist")
        print(user['errors'][0]['detail'])


def getFollowed(user_id) -> dict:
    """
    Returns a list of users the specified UserID is following
    :param user_id: The Twitter user ID
    :return: followed -> The list of followed users by the user
    """
    global users
    users = []
    list = client.get_users_following(id=user_id, max_results=1000)
    users = list['data']
    with open("followed.json", "w") as output:
        output.write(json.dumps(users))

    # check if exists "next_token" and get next page of users
    while 'next_token' in list['meta'].keys():
        next_token = list['meta']['next_token']
        list = client.get_users_following(id=user_id, max_results=1000, pagination_token=next_token)

        for e in list['data']:
            users.append(e)

        with open("followed.json", "w") as output:
            output.write(json.dumps(users))

        # double check for the last page
        if 'next_token' in list['meta'].keys():
            next_token = list['meta']['next_token']  # get next token

    return users


# Establish the url query for 500 results. This parameter is passed as GET
'''
def create_url():
    # Replace with user ID below
    user_id = 863407099
    return "https://api.twitter.com/2/users/{}/following?max_results=1000".format(user_id)


def get_params():
    return {"user.fields": "created_at"}


# Method used for authentication in order to make the request. Authentication is made with OAuth 2.0 Bearer Token
def bearer_oauth(r):
    """
    Method required by bearer token authentication.
    """

    r.headers["Authorization"] = f"Bearer {bearer_token}"
    r.headers["User-Agent"] = "v2FollowingLookupPython"
    return r

# Establish connection with paramenters
# RETURNS: The response in JSON format
def connect_to_endpoint(url, params):
    response = requests.request("GET", url, auth=bearer_oauth, params=params)
    #print(response.status_code)
    if response.status_code != 200:
        raise Exception(
            "Request returned an error: {} {}".format(
                response.status_code, response.text
            )
        )
    return response.json()
'''


def main():
    user_id = ""
    followed = []

    print("<> Welcome to ManUnfollows <>")

    while True:
        print("> To begin enter a valid Twitter username:")
        username = input()
        if len(username) == 0:
            print("Please enter a valid username")
        else:
            try:
                user_id = getUserID(username)
                followed = getFollowed(user_id)
                print(followed)
                break
            except Exception as e:
                print("Error: " + str(e))
                break
            # getFollowed(user_id)


if __name__ == "__main__":
    main()
