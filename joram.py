import re
from io import BytesIO
import requests
from bs4 import BeautifulSoup
import datetime
from PyPDF2 import PdfReader
from constants import PDF_GAS_PRICE_REGEX, JORAM_LINK, JORAM_PDF_LINK
from functions import replace_gas_keys_names

# Generator function to extract line by line text from PDF
def get_pdf_content_lines(pdf_raw_data):
    with BytesIO(pdf_raw_data) as f:
        pdf_reader = PdfReader(f)
        for page in pdf_reader.pages:
            for line in page.extract_text().splitlines():
                yield line


def get_sorted_pdf_links(joram_url):
    # Get the HTML response for the URL
    response = requests.get(joram_url, timeout=10)
    html = response.text

    # Parse the HTML content using BeautifulSoup
    html_content = BeautifulSoup(html, "html.parser")

    # Find all the links ending with '.pdf' from the HTML page
    pdf_links = [
        link for link in html_content.find_all("a") if link["href"].endswith(".pdf")
    ]

    # Sort the links based on the date in the href
    sorted_pdf_links = sorted(
        pdf_links,
        key=lambda link: datetime.datetime.strptime(
            re.search(r"\d{4}-\d{2}-\d{2}", link["href"]).group(), "%Y-%m-%d"
        ),
    )
    return sorted_pdf_links


# Function to extract the gas prices from the PDFs
def read_pdf_prices(pdf_url):
    discovered_prices = 0
    response = requests.get(pdf_url, timeout=10)
    for line in get_pdf_content_lines(response.content):
        if discovered_prices == 3:
            break
        match = re.search(PDF_GAS_PRICE_REGEX, line)
        if match:
            discovered_prices += 1
            yield match.groups()


# Retrieve pdf creation date
def retrieve_pdf_creation_date(pdf_url):
    response = requests.get(pdf_url, timeout=10)
    with BytesIO(response.content) as f:
        pdf_reader = PdfReader(f)
        # print(str(pdf_reader.metadata.creation_date))
        return pdf_reader.metadata.creation_date


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
    while len(sorted_pdf_links) > 0:
        newest_pdf_link = sorted_pdf_links.pop()
        newest_pdf_filename = newest_pdf_link["href"].split("/")[-1]
        newest_pdf_joram = JORAM_PDF_LINK.format(
            date=current_date, file=newest_pdf_filename
        )
        gas_prices = dict(read_pdf_prices(newest_pdf_joram))
        if gas_prices:
            break

    if not gas_prices:
        return None

    gas_prices = replace_gas_keys_names(gas_prices)
    return dict(
        gas_info=gas_prices, creation_date=retrieve_pdf_creation_date(newest_pdf_joram)
    )
