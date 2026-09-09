import re
from bs4 import BeautifulSoup
import requests

# Testaa tällä haluamasi yrityksen osoitteella (esim. oikea kampaamo tai ravintola)
url = 'https://esimerkki-kampaamo.fi'

print(f'Aloitetaan sivuston analysointi: {url}\n')
found_emails = set()

try:
  # 1. Haetaan pääsivu
  response = requests.get(
      url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'}
  )
  response.raise_for_status()
  soup = BeautifulSoup(response.text, 'html.parser')

  # 2. Etsitään sähköpostit etusivulta regexillä
  raw_emails = re.findall(
      r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', soup.text
  )

  # 3. Suodatetaan pois kuvatiedostot ja muut turhat päätteet
  valid_emails = [
      email
      for email in raw_emails
      if not email.lower().endswith(
          (
              '.png',
              '.jpg',
              '.jpeg',
              '.gif',
              '.webp',
              '.svg',
              '.css',
              '.js',
              '.pdf',
          )
      )
  ]
  found_emails.update(valid_emails)

  # 4. Jos etusivulta ei löydy, etsitään automaattisesti "Yhteystiedot" tai "Contact" -alasivu
  if not found_emails:
    print(
        '  -> Ei sähköpostia etusivulla. Etsitään yhteystietosivua linkkien'
        ' joukosta...'
    )
    for a in soup.find_all('a', href=True):
      href = a['href'].lower()
      if any(
          word in href for word in ['yhteys', 'contact', 'ota-yhteytta', 'about']
      ):
        contact_url = a['href']
        if not contact_url.startswith('http'):
          contact_url = url.rstrip('/') + '/' + contact_url.lstrip('/')

        try:
          sub_resp = requests.get(
              contact_url, timeout=5, headers={'User-Agent': 'Mozilla/5.0'}
          )
          sub_soup = BeautifulSoup(sub_resp.text, 'html.parser')
          sub_raw = re.findall(
              r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', sub_soup.text
          )
          sub_valid = [
              e
              for e in sub_raw
              if not e.lower().endswith(
                  (
                      '.png',
                      '.jpg',
                      '.jpeg',
                      '.gif',
                      '.webp',
                      '.svg',
                      '.css',
                      '.js',
                      '.pdf',
                  )
              )
          ]
          if sub_valid:
            found_emails.update(sub_valid)
            print(f'  -> Löytyi alasivulta: {contact_url}')
            break
        except:
          pass

  # 5. Tulokset
  print('\n----------------------------------------')
  if found_emails:
    print(f'Löydetyt sähköpostit osoitteesta {url}:')
    for email in sorted(found_emails):
      print(f'  - {email}')
  else:
    print('Sähköpostiosoitetta ei löytynyt automaattisesti tältä sivustolta.')
  print('----------------------------------------')

except requests.exceptions.RequestException as req_err:
  print(f'Verkkovirhe tai sivustoa ei tavoitettu: {req_err}')
except Exception as e:
  print(f'Virhe haussa: {e}')
