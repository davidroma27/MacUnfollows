import requests
import os
import json

# To set your environment variables in your terminal run the following line:
os.environ['BEARER_TOKEN'] = 'AAAAAAAAAAAAAAAAAAAAAGY0iAEAAAAAz%2BgzFSRNl35Kpx4ZrOxWks6XyCo%3Dx5dDctWITFVwOfhVbGPc7l2wlRBZQu0qkxJRkW8biAuz2InO51'
bearer_token = os.environ.get('BEARER_TOKEN')


# Establish the url query for 500 results. This parameter is passed as GET
def create_url():
    # Replace with user ID below
    user_id = 863407099
    return "https://api.twitter.com/2/users/{}/following?max_results=500".format(user_id)


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
    print(response.status_code)
    if response.status_code != 200:
        raise Exception(
            "Request returned an error: {} {}".format(
                response.status_code, response.text
            )
        )
    return response.json()


def main():
    url = create_url()
    params = get_params()
    json_response = connect_to_endpoint(url, params)
    print(json.dumps(json_response, indent=4, sort_keys=True))


if __name__ == "__main__":
    main()