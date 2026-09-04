import re
import logging
import datetime
import urllib.parse
import warnings
from io import BytesIO
import requests
from bs4 import BeautifulSoup
from PyPDF2 import PdfReader
from constants import PDF_GAS_PRICE_REGEX, JORAM_LINK, JORAM_PDF_LINK
from functions import replace_gas_keys_names

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
# Suppress verbose PDF library warnings
logging.getLogger("PyPDF2").setLevel(logging.ERROR)
warnings.filterwarnings("ignore", module="PyPDF2")


def fetch_pdf_bytes(pdf_url):
    # Properly encode URL to handle spaces and special characters.
    # We unquote first to avoid double encoding if the URL is already encoded.
    parts = urllib.parse.urlparse(pdf_url)
    unquoted_path = urllib.parse.unquote(parts.path)
    pdf_url = urllib.parse.urlunparse(
        parts._replace(path=urllib.parse.quote(unquoted_path))
    )
    response = requests.get(pdf_url, timeout=15)
    response.raise_for_status()
    return response.content


def pdf_text(pdf_bytes):
    all_text = ""
    with BytesIO(pdf_bytes) as f:
        pdf_reader = PdfReader(f)
        for page in pdf_reader.pages:
            text = page.extract_text()
            if text:
                all_text += text + "\n"
    return all_text


def pdf_creation_date(pdf_bytes):
    try:
        with BytesIO(pdf_bytes) as f:
            return PdfReader(f).metadata.creation_date
    except Exception as e:
        logging.error(f"Error retrieving PDF creation date: {e}")
        return None


def extract_gas_prices(pdf_bytes):
    all_text = pdf_text(pdf_bytes)

    # Normalize text to handle split lines (especially for Gasoline 95 in 2008)
    normalized_text = all_text.replace("\n", " ")
    # But we still want to try line by line for most cases as it's safer
    lines = all_text.splitlines()

    def price_of(match):
        name, price = match.groups()
        price = price.replace(" ", "")
        if "," in price and len(price.split(",")[1]) == 3:
            return name, price
        return None

    matches = []
    for line in lines:
        if len(matches) == 3:
            break
        match = re.search(PDF_GAS_PRICE_REGEX, line, re.IGNORECASE)
        if match:
            found = price_of(match)
            if found:
                matches.append(found)

    # If we didn't find 3 prices, try the normalized text (without line breaks).
    # Duplicates are possible; callers deduplicate with dict().
    if len(matches) < 3:
        all_matches = re.finditer(PDF_GAS_PRICE_REGEX, normalized_text, re.IGNORECASE)
        for match in all_matches:
            found = price_of(match)
            if found:
                matches.append(found)

    return matches


def read_pdf_prices(pdf_url):
    """Fetch a PDF and return a list of (name, price) tuples."""
    try:
        return extract_gas_prices(fetch_pdf_bytes(pdf_url))
    except Exception as e:
        logging.error(f"Error reading prices from PDF {pdf_url}: {e}")
        return []


def get_sorted_pdf_links(joram_url):
    try:
        # Get the HTML response for the URL
        response = requests.get(joram_url, timeout=15)
        response.raise_for_status()
        html = response.text

        # Parse the HTML content using BeautifulSoup
        html_content = BeautifulSoup(html, "html.parser")

        # Find all the links ending with '.pdf' from the HTML page
        pdf_links = [
            link
            for link in html_content.find_all("a")
            if link.get("href", "").endswith(".pdf")
        ]

        # Sort the links based on the date in the href
        def extract_date(link):
            match = re.search(r"\d{4}-\d{2}-\d{2}", link["href"])
            if match:
                try:
                    return datetime.datetime.strptime(match.group(), "%Y-%m-%d")
                except ValueError:
                    pass
            return datetime.datetime.min

        sorted_pdf_links = sorted(pdf_links, key=extract_date)
        return sorted_pdf_links
    except Exception as e:
        logging.error(f"Error fetching PDF links from {joram_url}: {e}")
        return []


# Retrieve gas prices
def retrieve_newest_pdf_gas_info():
    # Get the current date
    current_date = datetime.datetime.now()

    # JORAM URL for current year's PDFs
    joram_current_year_url = JORAM_LINK.format(date=current_date)

    sorted_pdf_links = get_sorted_pdf_links(joram_current_year_url)

    # Loop through the sorted PDF links and find the gas prices
    gas_prices = {}
    newest_pdf_joram = None
    creation_date = None

    while sorted_pdf_links:
        newest_pdf_link = sorted_pdf_links.pop()
        newest_pdf_filename = newest_pdf_link["href"].split("/")[-1]
        newest_pdf_joram = JORAM_PDF_LINK.format(
            date=current_date, file=newest_pdf_filename
        )

        logging.info(f"Checking PDF: {newest_pdf_joram}")
        try:
            # Fetch once and reuse the same bytes for prices and creation date
            pdf_bytes = fetch_pdf_bytes(newest_pdf_joram)
        except Exception as e:
            logging.error(f"Error reading PDF {newest_pdf_joram}: {e}")
            continue

        gas_prices = dict(extract_gas_prices(pdf_bytes))

        if gas_prices:
            creation_date = pdf_creation_date(pdf_bytes)
            if not creation_date:
                # Usually the creation date is present, but proceed anyway
                logging.warning(
                    f"Found prices but could not retrieve creation date for {newest_pdf_joram}"
                )
            break

    if not gas_prices:
        logging.info("No gas prices found in recent PDFs.")
        return None

    gas_prices = replace_gas_keys_names(gas_prices)

    if len(gas_prices) < 3:
        logging.warning(
            f"Expected 3 gas prices, but found {len(gas_prices)}: {list(gas_prices.keys())}"
        )

    return dict(
        gas_info=gas_prices, creation_date=creation_date, pdf_url=newest_pdf_joram
    )