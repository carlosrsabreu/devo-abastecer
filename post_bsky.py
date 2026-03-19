import os
import logging
from atproto import Client
from functions import format_social_media_message

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def create_client_bluesky():
    return Client()


def make_bsky_post_image(post_message, image_path):
    """
    Upload an image and post a message to Bluesky.
    """
    handle = os.getenv("BLUESKY_HANDLE")
    password = os.getenv("BLUESKY_APP_PASSWORD")

    if not handle or not password:
        logging.error("Bluesky handle or password not found in environment variables.")
        return None

    try:
        # Get Bluesky client
        client = create_client_bluesky()
        # Login
        client.login(handle, password)
        # Upload image
        with open(image_path, "rb") as f:
            image_data = f.read()
        image = client.upload_blob(image_data, content_type="image/png")
        # Post with image
        response = client.send_post(post_message, image=image)
        logging.info(f"Bluesky image post created successfully. URI: {response.uri}")
        return response
    except Exception as e:
        logging.error(f"Failed to post image to Bluesky: {e}")
        return None


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

        # Get Bluesky client
        client = create_client_bluesky()
        # Login
        client.login(handle, password)

        # Post to Bluesky
        response = client.send_post(post_message)
        logging.info(f"Bluesky post created successfully. URI: {response.uri}")
        return response
    except Exception as e:
        logging.error(f"Failed to post to Bluesky: {e}")
        return None
