import re
from io import BytesIO
import requests
from PyPDF2 import PdfFileReader
from constants import GASOLINE_95, DIESEL, COLORED_DIESEL

PDF_GAS_PRICE_REGEX = r'(?<=€ )([\d,]+)(?= por litro)'

def get_pdf_content_lines(pdf_raw_data):
    with BytesIO(pdf_raw_data) as f:
        pdf_reader = PdfFileReader(f)
        for page in pdf_reader.pages:
            for line in page.extractText().splitlines():
                yield line


def read_pdf_prices():
    response = requests.get('https://joram.madeira.gov.pt/joram/2serie/Ano%20de%202022/IISerie-138-2022-07-22Supl.pdf')
    prices = ()
    for line in get_pdf_content_lines(response.content):
        matches = re.search(PDF_GAS_PRICE_REGEX, line)
        if matches:
            prices += (matches.group(),)

    print(prices)



read_pdf_prices()

print(print())
