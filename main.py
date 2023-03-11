import os
import json
import tweepy
from config import *
from globals import *
from checkAccounts import check_inactive

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


def main():
    """
        MAIN flow of the app.
        Asks for a valid username in a infinite loop.
        Once a username is entered calls the following functions:
        1- getUserID
            > If username not exists, app will ask again for a username
        2- getFollowed
            > If user entered a private account, app will ask again for a non private account
    """

    user_id = ""
    # followed_users = []

    print("<> Welcome to MacUnfollows <>")
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
                    followed_users = getFollowed(user_id)
                    if len(followed_users) > 0:
                        print(followed_users)
                    else:
                        print("Please enter a valid username:")
                else:
                    print("Please enter a valid username:")
            except Exception as e:
                print("Error: " + str(e))
                break


if __name__ == "__main__":
    initialize()
    main()
    # getFollowed(1110821672507056128)
    #getUserID("macncheesys")
