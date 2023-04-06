import tweepy

# Paste here your Twitter API keys
BEARER_TOKEN = ""
consumer_key = ""
consumer_secret = ""
access_token = ""
access_token_secret = ""
# Paste here your oauth2 access token after you granted premissions via web browser
oauth2_access_token = ""


# For Twitter OAuth 2.0 Authorization Code Flow with PKCE (User Context) is necessary a handler
# You need to paste inside this functions the following tokens:
# > client_id
# > client_secret
def get_access_token():
    oauth2_user_handler = tweepy.OAuth2UserHandler(
        client_id="",
        redirect_uri="https://www.example.com",
        scope=["tweet.read", "users.read", "follows.write", "offline.access"],
        # Client Secret is only necessary if using a confidential client
        client_secret=""
    )

    print(oauth2_user_handler.get_authorization_url())
    full_url = input("Paste in the full URL after you authorized your App: ")
    O2_access_token = oauth2_user_handler.fetch_token(full_url)
    oauth2_access_token = O2_access_token["access_token"]
    print(oauth2_access_token)

    return oauth2_access_token
