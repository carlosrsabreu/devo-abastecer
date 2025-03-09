import os

import tweepy

from constants import (
    CURRENT_WEEK,
    START_DATE_KEY,
    DIESEL_TW,
    GASOLINE_95_TW,
    GASOLINE_98_TW,
    END_DATE_KEY,
    PREVIOUS_WEEK,
    DIESEL,
    GAS_KEY,
    GASOLINE_95,
    GASOLINE_98,
)


def create_client_twitter():
    return tweepy.Client(
        consumer_key=os.environ["CONSUMER_KEY"],
        consumer_secret=os.environ["CONSUMER_SECRET"],
        access_token=os.environ["ACCESS_TOKEN"],
        access_token_secret=os.environ["ACCESS_TOKEN_SECRET"],
    )


def gas_prices_message(price_current, price_previous):
    if price_current > price_previous:
        return f"{price_current}€   ⬆️   {price_previous}€"
    if price_current < price_previous:
        return f"{price_current}€   ⬇️️   {price_previous}€"
    if price_current == price_previous:
        return f"{price_current}€   =   {price_previous}€"


def create_api(client):
    auth = tweepy.OAuthHandler(
        client.consumer_key,
        client.consumer_secret,
    )
    auth.set_access_token(
        client.access_token,
        client.access_token_secret,
    )
    return tweepy.API(auth)


def post_image(tweet, image_path):
    # Get Twitter client
    client = create_client_twitter()
    # Create Twitter API
    api = create_api(client)
    # Upload image
    image = api.media_upload(image_path)
    # Post tweet
    return api.update_status(status=tweet, media_ids=[image.media_id])


def make_tweet(dict_prices):
    # Get Twitter client
    client = create_client_twitter()
    # Format Tweet
    tweet_message = "— Devo abastecer? ⛽️ \n\n"
    tweet_message += f"         {dict_prices[CURRENT_WEEK][START_DATE_KEY]}  |  {dict_prices[PREVIOUS_WEEK][START_DATE_KEY]}\n"
    tweet_message += "                      a         |            a\n"
    tweet_message += f"         {dict_prices[CURRENT_WEEK][END_DATE_KEY]}  |  {dict_prices[PREVIOUS_WEEK][END_DATE_KEY]}\n\n"
    tweet_message += f"{DIESEL_TW}{gas_prices_message(dict_prices[CURRENT_WEEK][GAS_KEY][DIESEL], dict_prices[PREVIOUS_WEEK][GAS_KEY][DIESEL])}\n"
    tweet_message += f"{GASOLINE_95_TW}{gas_prices_message(dict_prices[CURRENT_WEEK][GAS_KEY][GASOLINE_95], dict_prices[PREVIOUS_WEEK][GAS_KEY][GASOLINE_95])}\n"
    tweet_message += f"{GASOLINE_98_TW}{gas_prices_message(dict_prices[CURRENT_WEEK][GAS_KEY][GASOLINE_98], dict_prices[PREVIOUS_WEEK][GAS_KEY][GASOLINE_98])}\n"
    # Post Tweet
    client.create_tweet(text=tweet_message)
