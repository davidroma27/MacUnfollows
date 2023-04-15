import asyncio
from config import *
import globals
import actions


async def main():
    """
        MAIN flow of the app.\n
        1. Asks for a valid username in an infinite loop.\n
        2. Asks for a period to check if accounts are inactive
        Once a username is entered calls the following functions:\n
        -get_user_id()
            > If username not exists, app will ask again for a username
        -get_followed()
            > If user entered a private account, app will ask again for a non-private account
    """

    global username
    global period

    print("<> Welcome to MacUnfollows <>")
    print("> To begin enter a valid Twitter username:")

    # loop for control inputs flows
    username = input()
    while len(username) == 0:
        print("(!) - Username cannot be empty")
        username = input()

    print("> Please enter the maximum days for inactive accounts:")
    period = input()
    while len(period) == 0 or not period.isnumeric():
        print("(!) - Period cannot be empty and must be numeric")
        period = input()
    else:
        try:
            # Firstly check if there are pending accounts to unfollow
            await actions.check_json(int(period))
            user_id = await actions.get_user_id(username)
            if user_id[0] is not None:
                print("(i) - Getting followed accounts...")
                globals.followed_users = await actions.get_followed(user_id[0])
                n_followed = len(globals.followed_users[0])
                print(f"(i) - Found {n_followed} followed accounts")
                if globals.followed_users[0] is not None:
                    if len(globals.followed_users[0]) == 0:
                        print("(!) - This user does not follow any account")
                        print("> Please enter a valid username:")
                    else:
                        print("(i) - Looking for inactive accounts...")
                        await asyncio.shield(actions.check_inactive(globals.followed_users[0], period))
                elif globals.followed_users[1] is not None:
                    error = globals.followed_users[1]
                    if error[0]["title"] == 'Authorization Error':
                        print("(i) - The username entered is a private account")
                        print("> Please enter a valid username:")
            elif user_id[1] is not None:
                error = user_id[1]
                if error[0]["title"] == 'Not Found Error':
                    print("(i) - The username entered does not exist")
                    print("> Please enter a valid username:")
        except asyncio.TimeoutError:
            print("(!) - Timeout async error")
        except Exception as e:
            print(f"(!) ERROR: {e}")


if __name__ == "__main__":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())

    # getFollowed(1110821672507056128)
    # get_user_id("macncheesys")
    # asyncio.run(checkAccounts.check_inactive([], 365))
    # asyncio.run(actions.unfollow_user([956585870693453824]))
