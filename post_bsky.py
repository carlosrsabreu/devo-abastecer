import os
import logging
from atproto import Client
from functions import format_social_media_message

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def make_bsky_post(dict_prices):
    """
    Format and post a text message to Bluesky.
    """
    handle = os.getenv("BLUESKY_HANDLE")
    password = os.getenv("BLUESKY_APP_PASSWORD")

    if not handle or not password:
        logging.warning(
            "Bluesky handle or password not found in environment variables. Skipping Bluesky post."
        )
        return None

    try:
        # Format post
        post_message = format_social_media_message(dict_prices)
        if not post_message:
            return None

        # Login and post to Bluesky
        client = Client()
        client.login(handle, password)

        response = client.send_post(post_message)
        logging.info(f"Bluesky post created successfully. URI: {response.uri}")
        return response
    except Exception as e:
        logging.error(f"Failed to post to Bluesky: {e}")
        return None
