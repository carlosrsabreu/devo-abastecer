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


def create_api(client):
    if not client:
        return None

    auth = tweepy.OAuthHandler(
        client.consumer_key,
        client.consumer_secret,
    )
    auth.set_access_token(
        client.access_token,
        client.access_token_secret,
    )
    return tweepy.API(auth)


def post_image(tweet_message, image_path):
    """
    Post a tweet with an image.
    """
    client = create_client_twitter()
    if not client:
        return None

    api = create_api(client)
    if not api:
        return None

    try:
        # Upload image
        image = api.media_upload(image_path)
        # Post tweet
        response = api.update_status(status=tweet_message, media_ids=[image.media_id])
        logging.info("Twitter image post created successfully.")
        return response
    except Exception as e:
        logging.error(f"Failed to post image to Twitter: {e}")
        return None


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
