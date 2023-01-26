import re
from io import BytesIO
import requests
from bs4 import BeautifulSoup
import datetime
from PyPDF2 import PdfReader
from constants import GASOLINE_95, DIESEL, COLORED_DIESEL, PDF_GAS_PRICE_REGEX

# Get the current year
current_year = str(datetime.datetime.now().year)

# JORAM URL for current year's PDFs
url = f"https://joram.madeira.gov.pt/joram/2serie/Ano%20de%20{current_year}/"

response = requests.get(url)
html = response.text
soup = BeautifulSoup(html, "html.parser")
links = soup.find_all("a")

pdf_links = [link for link in links if link["href"].endswith(".pdf")]
sorted_pdf_links = sorted(
    pdf_links,
    key=lambda link: datetime.datetime.strptime(
        re.search(r"\d{4}-\d{2}-\d{2}", link["href"]).group(), "%Y-%m-%d"
    ),
)
newest_pdf_link = sorted_pdf_links[-1]
newest_pdf_filename = newest_pdf_link["href"].split("/")[-1]

# FIXME (DEBUG) Print se the filename to scrape the content
print(newest_pdf_filename)
# FIXME (DEBUG): Working link to Joram PDF
debug_pdf_joram = "https://joram.madeira.gov.pt/joram/2serie/Ano%20de%202022/IISerie-138-2022-07-22Supl.pdf"

# Get the latest PDF from the JORAM website
newest_pdf_joram = f"https://joram.madeira.gov.pt/joram/2serie/Ano%20de%20{current_year}/{newest_pdf_filename}"


def get_pdf_content_lines(pdf_raw_data):
    with BytesIO(pdf_raw_data) as f:
        pdf_reader = PdfReader(f)
        for page in pdf_reader.pages:
            for line in page.extract_text().splitlines():
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
            yield matches.groups()


if __name__ == "__main__":
    print(dict(read_pdf_prices(newest_pdf_joram)))
    # FIXME (DEBUG): Print the hardcoded link
    print(dict(read_pdf_prices(debug_pdf_joram)))
