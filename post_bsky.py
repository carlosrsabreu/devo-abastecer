import os
from atproto import Client

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


def create_client_bluesky():
    return Client()


def gas_prices_message(price_current, price_previous):
    if price_current > price_previous:
        return f"{price_current}€   ⬆️   {price_previous}€"
    if price_current < price_previous:
        return f"{price_current}€   ⬇️️   {price_previous}€"
    if price_current == price_previous:
        return f"{price_current}€   =   {price_previous}€"


def make_bsky_post_image(post, image_path):
    # Get Bluesky client
    client = create_client_bluesky()
    # Login using environment variables
    client.login(os.environ["BLUESKY_HANDLE"], os.environ["BLUESKY_APP_PASSWORD"])
    # Upload image
    with open(image_path, "rb") as f:
        image_data = f.read()
    image = client.upload_blob(image_data, content_type="image/jpeg")
    # Post with image
    return client.send_post(post, image=image)
    print(f"Post created successfully. URI: {post.uri}")


def make_bsky_post(dict_prices):
    # Get Bluesky client
    client = create_client_bluesky()
    # Login using environment variables
    client.login(os.environ["BLUESKY_HANDLE"], os.environ["BLUESKY_APP_PASSWORD"])
    # Format post
    post_message = "— Devo abastecer? ⛽️ \n\n"
    post_message += f"         {dict_prices[CURRENT_WEEK][START_DATE_KEY]}  |  {dict_prices[PREVIOUS_WEEK][START_DATE_KEY]}\n"
    post_message += "                      a         |            a\n"
    post_message += f"         {dict_prices[CURRENT_WEEK][END_DATE_KEY]}  |  {dict_prices[PREVIOUS_WEEK][END_DATE_KEY]}\n\n"
    post_message += f"{DIESEL_TW}{gas_prices_message(dict_prices[CURRENT_WEEK][GAS_KEY][DIESEL], dict_prices[PREVIOUS_WEEK][GAS_KEY][DIESEL])}\n"
    post_message += f"{GASOLINE_95_TW}{gas_prices_message(dict_prices[CURRENT_WEEK][GAS_KEY][GASOLINE_95], dict_prices[PREVIOUS_WEEK][GAS_KEY][GASOLINE_95])}\n"
    post_message += f"{GASOLINE_98_TW}{gas_prices_message(dict_prices[CURRENT_WEEK][GAS_KEY][GASOLINE_98], dict_prices[PREVIOUS_WEEK][GAS_KEY][GASOLINE_98])}\n"
    # Post to Bluesky
    return client.send_post(post_message)
    print(f"Post created successfully. URI: {post.uri}")
