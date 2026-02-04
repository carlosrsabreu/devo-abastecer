import os
import requests

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

# Replace with your Page ID and Access Token
PAGE_ID = os.environ["FACEBOOK_PAGE_ID"]
ACCESS_TOKEN = os.environ["FACEBOOK_ACCESS_TOKEN"]

GRAPH_API_URL = "https://graph.facebook.com/v22.0"


def gas_prices_message(price_current, price_previous):
    if price_current > price_previous:
        return f"{price_current}€   ⬆️   {price_previous}€"
    if price_current < price_previous:
        return f"{price_current}€   ⬇️️   {price_previous}€"
    if price_current == price_previous:
        return f"{price_current}€   =   {price_previous}€"


def post_text_to_facebook(message):
    """
    Post a text message to the Facebook page.
    """
    url = f"{GRAPH_API_URL}/{PAGE_ID}/feed"
    payload = {
        "message": message,
        "access_token": ACCESS_TOKEN,
    }

    response = requests.post(url, data=payload, timeout=10)

    if response.status_code == 200:
        print("Text post published successfully!")
        return response.json()
    else:
        print(f"Failed to post text: {response.json()}")
        return None


def post_image_to_facebook(image_path, caption=""):
    """
    Post an image with an optional caption to the Facebook page.
    """
    url = f"{GRAPH_API_URL}/{PAGE_ID}/photos"
    payload = {
        "caption": caption,
        "access_token": ACCESS_TOKEN,
    }

    with open(image_path, "rb") as f:
        files = {
            "source": f,
        }

        response = requests.post(url, data=payload, files=files, timeout=10)

    if response.status_code == 200:
        print("Image post published successfully!")
        return response.json()
    else:
        print(f"Failed to post image: {response.json()}")
        return None


def make_facebook_post(dict_prices):
    """
    Format and post a message to the Facebook page.
    """
    # Format post
    post_message = "— Devo abastecer? ⛽️ \n\n"
    post_message += f"         {dict_prices[CURRENT_WEEK][START_DATE_KEY]}  |  {dict_prices[PREVIOUS_WEEK][START_DATE_KEY]}\n"
    post_message += "                      a         |            a\n"
    post_message += f"         {dict_prices[CURRENT_WEEK][END_DATE_KEY]}  |  {dict_prices[PREVIOUS_WEEK][END_DATE_KEY]}\n\n"
    post_message += f"{DIESEL_TW}{gas_prices_message(dict_prices[CURRENT_WEEK][GAS_KEY][DIESEL], dict_prices[PREVIOUS_WEEK][GAS_KEY][DIESEL])}\n"
    post_message += f"{GASOLINE_95_TW}{gas_prices_message(dict_prices[CURRENT_WEEK][GAS_KEY][GASOLINE_95], dict_prices[PREVIOUS_WEEK][GAS_KEY][GASOLINE_95])}\n"
    post_message += f"{GASOLINE_98_TW}{gas_prices_message(dict_prices[CURRENT_WEEK][GAS_KEY][GASOLINE_98], dict_prices[PREVIOUS_WEEK][GAS_KEY][GASOLINE_98])}\n"
    post_message += f"\n\n"
    post_message += f"#Portugal #Madeira ##IlhaDaMadeira  #Funchal #Combustível #Fuel\n"
    # Post the message
    return post_text_to_facebook(post_message)
