from requests_oauthlib import OAuth1Session
from django.conf import settings
import json


class Tweet():
    _instance = None
    CONSUMER_KEY = "VyaFOhtvBT1Lh6l7z1PYoMH3n"
    CONSUMER_SECRET = "fzJGROlVIkJEF2qk9mZFvAZYyXLAWDB4XzAB72r2NFJikq1QYK"

    def __new__(cls):
        if cls._instance is None:
            print("Creating the Tweet object")
            cls._instance = super(Tweet, cls).__new__(cls)
            cls._instance.oauth = None
            # Use settings if available, otherwise use hardcoded values
            if hasattr(settings, 'X_API_KEY') and settings.X_API_KEY:
                cls._instance.consumer_key = settings.X_API_KEY
                cls._instance.consumer_secret = settings.X_API_SECRET
                cls._instance.access_token = settings.X_ACCESS_TOKEN
                cls._instance.access_token_secret = settings.X_ACCESS_SECRET
            else:
                cls._instance.consumer_key = cls.CONSUMER_KEY
                cls._instance.consumer_secret = cls.CONSUMER_SECRET
                cls._instance.access_token = None
                cls._instance.access_token_secret = None
        return cls._instance

    def authenticate(self):
        """Authenticate with Twitter API using OAuth1"""
        # If we have access tokens from settings, use them directly
        if self.access_token and self.access_token_secret:
            self.oauth = OAuth1Session(
                self.consumer_key,
                client_secret=self.consumer_secret,
                resource_owner_key=self.access_token,
                resource_owner_secret=self.access_token_secret,
            )
            return self.oauth

        # Otherwise, use the interactive OAuth flow
        request_token_url = (
            "https://api.twitter.com/oauth/request_token?"
            "oauth_callback=oob&x_auth_access_type=write"
        )
        oauth = OAuth1Session(
            self.consumer_key, client_secret=self.consumer_secret
        )

        try:
            fetch_response = oauth.fetch_request_token(request_token_url)
        except ValueError:
            print(
                "There may have been an issue with the consumer_key "
                "or consumer_secret you entered"
            )
            return None

        resource_owner_key = fetch_response.get("oauth_token")
        resource_owner_secret = fetch_response.get("oauth_token_secret")
        print("Got oauth token: %s" % resource_owner_key)

        # Step 2 Get authorization
        base_authorization_url = "https://api.twitter.com/oauth/authorize"
        authorization_url = oauth.authorization_url(base_authorization_url)
        print("Please go here and authorize: %s" % authorization_url)
        verifier = input("Paste the pin here: ")

        # Get the access token
        access_token_url = "https://api.twitter.com/oauth/access_token"
        oauth = OAuth1Session(
            self.consumer_key,
            client_secret=self.consumer_secret,
            resource_owner_key=resource_owner_key,
            resource_owner_secret=resource_owner_secret,
            verifier=verifier,
        )
        oauth_tokens = oauth.fetch_access_token(access_token_url)

        access_token = oauth_tokens["oauth_token"]
        access_token_secret = oauth_tokens["oauth_token_secret"]

        # Make the request
        self.oauth = OAuth1Session(
            self.consumer_key,
            client_secret=self.consumer_secret,
            resource_owner_key=access_token,
            resource_owner_secret=access_token_secret,
        )
        return self.oauth

    def make_tweet(self, tweet_data):
        """Post a tweet using Twitter API v2"""
        if self.oauth is None:
            if not self.authenticate():
                raise ValueError("Authentication failed!")

        # Making the request
        response = self.oauth.post(
            "https://api.twitter.com/2/tweets",
            json=tweet_data,
        )

        if response.status_code != 201:
            raise Exception(
                "Request returned an error: {} {}".format(
                    response.status_code, response.text
                )
            )

        print("Response code: {}".format(response.status_code))

        # Saving the response as JSON
        json_response = response.json()
        print(json.dumps(json_response, indent=4, sort_keys=True))
        return json_response

    @staticmethod
    def tweet_article(article):
        """Tweet when an article is approved"""
        try:
            tweet_client = Tweet()

            # Shorten content for X (280 chars max)
            snippet = (
                article.content[:200] + "..."
                if len(article.content) > 200
                else article.content
            )

            tweet_text = (
                f" New Article Published!\n\n"
                f"{article.title}\n\n"
                f"{snippet}"
            )

            tweet_data = {"text": tweet_text}
            tweet_client.make_tweet(tweet_data)

        except Exception as e:
            print(f"Twitter error when posting article: {e}")