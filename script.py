# Importing BeautifulSoup class from the bs4 module
from bs4 import BeautifulSoup

# Importing the HTTP library
import requests as req
  
# Requesting for the website
Web = req.get('https://www.madeira.gov.pt/drett')
  
# Creating a BeautifulSoup object and specifying the parser
S = BeautifulSoup(Web.text, 'html.parser')
  
# Find the id with gas info
spanWithGasInfo = S.find('span', {'id':'dnn_ctr9883_View_D1_dlstInformacaoOne_Conteudo_0'})

# Get the text without html tags
gasInfo = spanWithGasInfo.get_text('\n', strip=True)

# TODO: Define gas price class and parse it to check if prices increased or decreased
class GasPrice:
  def __init__(self, name, price):
    self.name = name
    self.price = price
 
