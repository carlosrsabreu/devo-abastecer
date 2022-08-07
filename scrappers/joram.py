import re
from io import BytesIO
import requests
from PyPDF2 import PdfFileReader

# TODO: Get url with current year
#       Get all pdf's with the current date
#       Search for gas prices
#       Script will run only on friday every 1h to check for new documents


PDF_GAS_PRICE_REGEX = r'(?<=€ )([\d,]+)(?= por litro)'

# TODO: Only for example. Make this url dynamic with current year and year
JORAM_URL = 'https://joram.madeira.gov.pt/joram/2serie/Ano%20de%202022/IISerie-138-2022-07-22Supl.pdf'


def get_pdf_content_lines(pdf_raw_data):
    with BytesIO(pdf_raw_data) as f:
        pdf_reader = PdfFileReader(f)
        for page in pdf_reader.pages:
            for line in page.extractText().splitlines():
                yield line


def read_pdf_prices(url):
    """
    Reads a pdf line by line and verify if contains a gas price.
    The prices are always in the same order just need to make a match.
    """
    response = requests.get(url)
    prices = ()
    for line in get_pdf_content_lines(response.content):
        matches = re.search(PDF_GAS_PRICE_REGEX, line)
        if matches:
            prices += (matches.group(),)

    print(prices)


read_pdf_prices(JORAM_URL)
