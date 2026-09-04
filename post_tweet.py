import os
import logging
import tweepy

from functions import format_social_media_message

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def create_client_twitter():
    consumer_key = os.getenv("CONSUMER_KEY")
    consumer_secret = os.getenv("CONSUMER_SECRET")
    access_token = os.getenv("ACCESS_TOKEN")
    access_token_secret = os.getenv("ACCESS_TOKEN_SECRET")

    if not all([consumer_key, consumer_secret, access_token, access_token_secret]):
        logging.error("Twitter credentials not found in environment variables.")
        return None

    return tweepy.Client(
        consumer_key=consumer_key,
        consumer_secret=consumer_secret,
        access_token=access_token,
        access_token_secret=access_token_secret,
    )


def make_tweet(dict_prices):
    """
    Format and post a text tweet.
    """
    client = create_client_twitter()
    if not client:
        logging.warning("Twitter client not initialized. Skipping Twitter post.")
        return None

    # Format Tweet
    tweet_message = format_social_media_message(dict_prices)
    if not tweet_message:
        return None

    try:
        # Post Tweet
        response = client.create_tweet(text=tweet_message)
        logging.info("Twitter post created successfully.")
        return response
    except Exception as e:
        logging.error(f"Failed to post to Twitter: {e}")
        return None
