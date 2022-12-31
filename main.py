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
    try:
        if 'data' in user:
            user_id = user['data']['id']
            print(f"The {username}'s ID is : {user_id}")
            return user_id
        elif 'errors' in user:
            if user['errors'][0]['title'] == 'Not Found Error':
                print("The username entered does not exist")

    except Exception as e:
        print(f"Error: {e}")



def getFollowed(user_id) -> dict:
    """
    Returns a list of users the specified UserID is following
    :param user_id: The Twitter user ID
    :return: followed -> The list of followed users by the user
    """
    global users
    users = []
    list = []

    try:
        list = client.get_users_following(id=user_id, max_results=1000)

        # Check if list is returning data or returning errors
        if "data" in list:
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
        elif 'errors' in list:
            title = list['errors'][0]['title']
            if title == 'Authorization Error':
                print("The username entered is a private account")

    except Exception as e:
        print(f"Error: {e}")

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
    print("> To begin enter a valid Twitter username:")

    # loop for control username input
    while True:
        username = input()
        if len(username) == 0:
            print("Please enter a valid username:")
        else:
            try:
                user_id = getUserID(username)
                if user_id is not None:
                    followed = getFollowed(user_id)
                    if len(followed) > 0:
                        print(followed)
                    else:
                        print("Please enter a valid username:")
                else:
                    print("Please enter a valid username:")
            except Exception as e:
                print("Error: " + str(e))
                break


if __name__ == "__main__":
    main()
    #getFollowed(1110821672507056128)
    #getUserID("12ju1i332u")
