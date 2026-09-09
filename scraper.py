import re
import requests
from bs4 import BeautifulSoup

# Esimerkkisivusto, jolta tietoja haetaan (vaihda tähän haluamasi yrityksen osoite)
url = 'https://esimerkki-yritys.fi'

try:
  response = requests.get(url, timeout=10)
  soup = BeautifulSoup(response.text, 'html.parser')

  # Etsitään sähköpostit sivun tekstistä regexillä
  emails = set(
      re.findall(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', soup.text)
  )

  print(f'Löydetyt sähköpostit osoitteesta {url}:')
  for email in emails:
    print(email)

except Exception as e:
  print(f'Virhe haussa: {e}')
