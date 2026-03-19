import re
import logging
import datetime
from io import BytesIO
import requests
from bs4 import BeautifulSoup
from PyPDF2 import PdfReader
from constants import PDF_GAS_PRICE_REGEX, JORAM_LINK, JORAM_PDF_LINK
from functions import replace_gas_keys_names

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


# Generator function to extract line by line text from PDF
def get_pdf_content_lines(pdf_raw_data):
    try:
        with BytesIO(pdf_raw_data) as f:
            pdf_reader = PdfReader(f)
            for page in pdf_reader.pages:
                text = page.extract_text()
                if text:
                    for line in text.splitlines():
                        yield line
    except Exception as e:
        logging.error(f"Error reading PDF content: {e}")


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
                return datetime.datetime.strptime(match.group(), "%Y-%m-%d")
            return datetime.datetime.min

        sorted_pdf_links = sorted(pdf_links, key=extract_date)
        return sorted_pdf_links
    except Exception as e:
        logging.error(f"Error fetching PDF links from {joram_url}: {e}")
        return []


# Function to extract the gas prices from the PDFs
def read_pdf_prices(pdf_url):
    try:
        discovered_prices = 0
        response = requests.get(pdf_url, timeout=15)
        response.raise_for_status()
        for line in get_pdf_content_lines(response.content):
            if discovered_prices == 3:
                break
            match = re.search(PDF_GAS_PRICE_REGEX, line)
            if match:
                discovered_prices += 1
                yield match.groups()
    except Exception as e:
        logging.error(f"Error reading prices from PDF {pdf_url}: {e}")


# Retrieve pdf creation date
def retrieve_pdf_creation_date(pdf_url):
    try:
        response = requests.get(pdf_url, timeout=15)
        response.raise_for_status()
        with BytesIO(response.content) as f:
            pdf_reader = PdfReader(f)
            return pdf_reader.metadata.creation_date
    except Exception as e:
        logging.error(f"Error retrieving PDF creation date from {pdf_url}: {e}")
        return None


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

    while len(sorted_pdf_links) > 0:
        newest_pdf_link = sorted_pdf_links.pop()
        newest_pdf_filename = newest_pdf_link["href"].split("/")[-1]
        newest_pdf_joram = JORAM_PDF_LINK.format(
            date=current_date, file=newest_pdf_filename
        )

        logging.info(f"Checking PDF: {newest_pdf_joram}")
        gas_prices = dict(read_pdf_prices(newest_pdf_joram))

        if gas_prices:
            creation_date = retrieve_pdf_creation_date(newest_pdf_joram)
            if creation_date:
                break
            else:
                # If we found prices but couldn't get creation date, we might still want to proceed
                # or try another PDF. Usually creation date should be there.
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

    return dict(gas_info=gas_prices, creation_date=creation_date)
