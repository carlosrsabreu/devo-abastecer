# Values
END_DATE_KEY = "End date"
GAS_KEY = "Gas"
PDF_URL_KEY = "PDF URL"
START_DATE_KEY = "Start date"
CURRENT_WEEK = "current"
PREVIOUS_WEEK = "previous"
# Constants
DIFFERENCE_95_98_PRICE = 0.15
# Files
CURRENT_GAS_INFO_FILE = "gas_info.json"
CURRENT_GAS_HISTORY_JSON_FILE = "history/gas_info_history.json"
CURRENT_GAS_HISTORY_CSV_FILE = "history/gas_info_history.csv"
CURRENT_GAS_HISTORY_PLOT_FILE = "history/gas_history.png"
# Gas
DIESEL = "Gasóleo Rodoviário"
GASOLINE_95 = "Gasolina IO95"
GASOLINE_98 = "Gasolina IO98"
COLORED_DIESEL = "Gasóleo Colorido e Marcado"
# Gas (for Tweet)
DIESEL_TW = "Gasóleo         "
GASOLINE_95_TW = "Gasolina 95  "
GASOLINE_98_TW = "Gasolina 98  "

# PDF_GAS_PRICE_REGEX = r'(?<=€ )([\d,]+)(?= por litro)'
PDF_GAS_PRICE_REGEX = r"(G\s*a\s*s\s*o\s*l\s*i\s*n\s*[as]\s*s\s*u\s*p\s*e\s*r(?:\s*s\s*e\s*m\s*c\s*h\s*u\s*m\s*b\s*o\s*I\s*O\s*9\s*5)?|G\s*a\s*s\s*[oó]\s*l\s*e\s*o\s*R\s*o\s*d\s*o\s*v\s*i\s*[aá]\s*r\s*i\s*o|G\s*a\s*s\s*[oó]\s*l\s*e\s*o\s*c\s*o\s*l\s*o\s*r\s*i\s*d\s*o\s*e\s*m\s*a\s*r\s*c\s*a\s*d\s*o)[\s\.…€]*(\d{1}\s*,\s*[\d\s]{3,5})"


# History plot
HISTORY_PLOT_LABEL_GASOLINA_IO95 = "Gasolina IO95"
HISTORY_PLOT_LABEL_GASOLINA_IO98 = "Gasolina IO98"
HISTORY_PLOT_LABEL_GASOLEO_RODOVIARIO = "Gasoleo Rodoviario"
HISTORY_PLOT_Y_LABEL = "Preço (€)"
HISTORY_PLOT_X_LABEL = "Data"

# CSV columns
COLUMN_START_DATE = "start_date"
COLUMN_END_DATE = "end_date"
COLUMN_GASOLINA_IO95 = "gasolina_IO95"
COLUMN_GASOLINA_IO98 = "gasolina_IO98"
COLUMN_GASOLEO_RODOVIARIO = "gasoleo_rodoviario"

# Tweets
TWEET_HISTORY = (
    "Variação dos preços dos combustíveis na Madeira, de {start_date} a {end_date}."
)

# JORAM link 2023 - For Debugging
# JORAM_LINK = "https://joram.madeira.gov.pt/joram/2serie/Ano%20de%202023"
# JORAM_PDF_LINK = "https://joram.madeira.gov.pt/joram/2serie/Ano%20de%202023/{file}"

# JORAM link
JORAM_LINK = "https://joram.madeira.gov.pt/joram/2serie/Ano%20de%20{date:%Y}"
JORAM_PDF_LINK = "https://joram.madeira.gov.pt/joram/2serie/Ano%20de%20{date:%Y}/{file}"
