import os
import logging
import requests

from functions import format_social_media_message

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

# Get Page ID and Access Token from environment variables
PAGE_ID = os.getenv("FACEBOOK_PAGE_ID")
ACCESS_TOKEN = os.getenv("FACEBOOK_ACCESS_TOKEN")

GRAPH_API_URL = "https://graph.facebook.com/v22.0"


def post_text_to_facebook(message):
    """
    Post a text message to the Facebook page.
    """
    if not PAGE_ID or not ACCESS_TOKEN:
        logging.warning(
            "Facebook Page ID or Access Token not found in environment variables. Skipping Facebook post."
        )
        return None

    url = f"{GRAPH_API_URL}/{PAGE_ID}/feed"
    payload = {
        "message": message,
        "access_token": ACCESS_TOKEN,
    }

    try:
        response = requests.post(url, data=payload, timeout=10)

        if response.status_code == 200:
            logging.info("Facebook text post published successfully!")
            return response.json()
        else:
            logging.error(f"Failed to post text to Facebook: {response.json()}")
            return None
    except Exception as e:
        logging.error(f"Failed to post text to Facebook: {e}")
        return None


def post_image_to_facebook(image_path, caption=""):
    """
    Post an image with an optional caption to the Facebook page.
    """
    if not PAGE_ID or not ACCESS_TOKEN:
        logging.error(
            "Facebook Page ID or Access Token not found in environment variables."
        )
        return None

    url = f"{GRAPH_API_URL}/{PAGE_ID}/photos"
    payload = {
        "caption": caption,
        "access_token": ACCESS_TOKEN,
    }

    try:
        with open(image_path, "rb") as f:
            files = {
                "source": f,
            }

            response = requests.post(url, data=payload, files=files, timeout=10)

        if response.status_code == 200:
            logging.info("Facebook image post published successfully!")
            return response.json()
        else:
            logging.error(f"Failed to post image to Facebook: {response.json()}")
            return None
    except Exception as e:
        logging.error(f"Failed to post image to Facebook: {e}")
        return None


def make_facebook_post(dict_prices):
    """
    Format and post a message to the Facebook page.
    """
    # Format post
    message = format_social_media_message(dict_prices)
    if not message:
        return None

    message += "\n\n"
    message += "#Portugal #Madeira #IlhaDaMadeira #Funchal #Combustível #Fuel\n"

    # Post the message
    return post_text_to_facebook(message)
