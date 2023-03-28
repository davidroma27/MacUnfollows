import asyncio
import os
import json
import tweepy
from config import *
import globals
import actions

# To set your environment variables in your terminal run the following line:
os.environ['BEARER_TOKEN'] = BEARER_TOKEN
bearer_token = os.environ.get('BEARER_TOKEN')

# Configuring tweepy client
client = tweepy.Client(bearer_token=bearer_token, consumer_key=consumer_key, consumer_secret=consumer_secret,
                       access_token=access_token, access_token_secret=access_token_secret, return_type=dict)


def getUserID(username) -> tuple:
    """
        Function to get User ID
    :param username: The Twitter username
    :return: user_id -> The ID of the user
    """
    global user_id
    global errors
    user_id = None
    errors = None

    user = client.get_user(username=username)
    try:
        if 'data' in user:
            user_id = user['data']['id']
            print(f"The {username}'s ID is : {user_id}")
        elif 'errors' in user:
            errors = user['errors']
    except tweepy.errors.TweepyException:
        if tweepy.errors.TooManyRequests:
            print("(i) - Twitter API rate limit has reached. Should wait 15 mins to rerun")
    except Exception as e:
        print(f"Error: {e}")
    return user_id, errors

def getFollowed(user_id) -> tuple:
    """
    Returns a list of users the specified UserID is following
    :param user_id: The Twitter user ID
    :return: followed -> The list of followed users by the user
    """
    global users
    global errors
    users = []
    errors = None

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
            errors = list['errors'][0]
    except tweepy.errors.TweepyException:
        if tweepy.errors.TooManyRequests:
            print("(i) - Twitter API rate limit has reached. Should wait 15 mins to rerun")
    except Exception as e:
        print(f"Error: {e}")

    return users, errors


async def main():
    """
        MAIN flow of the app.
        Asks for a valid username in a infinite loop.
        Once a username is entered calls the following functions:
        1- getUserID
            > If username not exists, app will ask again for a username
        2- getFollowed
            > If user entered a private account, app will ask again for a non private account
    """

    print("<> Welcome to MacUnfollows <>")
    print("> To begin enter a valid Twitter username:")

    # loop for control inputs flows
    global username
    global period

    username = input()
    while len(username) == 0:
        print("! - Username cannot be empty")
        username = input()

    print("> Please enter the maximum days for inactive accounts:")
    period = input()
    while len(period) == 0 or not period.isnumeric():
        print("! - Period cannot be empty and must be numeric")
        period = input()
    else:
        try:
            user_id = getUserID(username)
            if user_id[0] is not None:
                globals.followed_users = getFollowed(user_id[0])
                if globals.followed_users[0] is not None:
                    if len(globals.followed_users[0]) == 0:
                        print("! - This user does not follow any account")
                        print("> Please enter a valid username:")
                    else:
                        print(username)
                        print(period)
                        try:
                            await asyncio.shield(actions.check_inactive(globals.followed_users[0], period))
                        except asyncio.TimeoutError:
                            print("! - Timeout async error")
                elif globals.followed_users[1] is not None:
                    error = globals.followed_users[1]
                    if error[0]["title"] == 'Authorization Error':
                        print("The username entered is a private account")
                        print("> Please enter a valid username:")
            elif user_id[1] is not None:
                error = user_id[1]
                if error[0]["title"] == 'Not Found Error':
                    print("The username entered does not exist")
                    print("> Please enter a valid username:")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    # asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    # asyncio.run(main())

    # getFollowed(1110821672507056128)
    #getUserID("macncheesys")
    # asyncio.run(checkAccounts.check_inactive([], 365))
    asyncio.run(actions.unfollow_user([131283008]))