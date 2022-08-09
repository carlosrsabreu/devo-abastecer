#!/bin/python
import re
from io import BytesIO
import requests
from PyPDF2 import PdfFileReader
from constants import GASOLINE_95, DIESEL, COLORED_DIESEL

# TODO: Get url with current year
#       Get all pdf's with the current date
#       Search for gas prices
#       Script will run only on friday every 1h to check for new documents

PDF_GAS_PRICE_REGEX = r'(?<=€ )([\d,]+)(?= por litro)'

# TODO: Only for example. Make this url dynamic with current year and date
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
    discovered_prices = 0
    response = requests.get(url)
    for line in get_pdf_content_lines(response.content):
        if discovered_prices == 3:
            break
        matches = re.search(PDF_GAS_PRICE_REGEX, line)
        if matches:
            discovered_prices += 1
            yield matches.group()



def get_gas_prices(url):
    """
    Attach the prices to a label
    :param url: Pdf url that contains gas prices
    :return: {'Gasolina IO95': '1,889', 'Gasóleo Rodoviário': '1,789', 'Gasóleo Colorido e Marcado': '1,425'}
    """
    labels = (GASOLINE_95, DIESEL, COLORED_DIESEL)

    return dict(zip(labels, read_pdf_prices(url)))


if __name__ == '__main__':
    print(get_gas_prices(JORAM_URL))
