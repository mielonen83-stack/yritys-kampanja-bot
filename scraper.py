import csv
import re
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS
import requests

# ==========================================
# MÄÄRITÄ HAKUSANA TÄHÄN (Mitä etsitään ja mistä)
# ==========================================
HAKUSANA = 'kampaamo Joensuu'
MAX_TULOKSET = 5  # Kuinka monta yritystä haetaan kerralla

print(
    f"Etsitään automaattisesti verkosta hakusanalla: '{HAKUSANA}'...\n"
)
found_companies = []

try:
  with DDGS() as ddgs:
    results = ddgs.text(HAKUSANA, max_results=MAX_TULOKSET)
    for r in results:
      href = r.get('href')
      if href:
        # Suodatetaan isot somesivut ja hakemistot pois, jotta saadaan aidot yrityssivustot
        ohita = [
            'facebook.com',
            'instagram.com',
            'finder.fi',
            'eniro.fi',
            'wikipedia.org',
            'youtube.com',
            'tiktok.com',
            'tripadvisor.fi',
            'fonecta.fi',
        ]
        if not any(s in href for s in ohita):
          found_companies.append(href)
except Exception as e:
  print(f'Virhe haussa: {e}')

print(f'Löytyi {len(found_companies)} potentiaalista yrityssivustoa. Aloitetaan sähköpostien haku...\n')

all_results = []

for url in found_companies:
  print(f'Tutkitaan sivustoa: {url}')
  found_emails = set()

  try:
    # 1. Haetaan pääsivu
    response = requests.get(
        url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'}
    )
    soup = BeautifulSoup(response.text, 'html.parser')

    # Etsitään sähköpostit etusivulta
    raw_emails = re.findall(
        r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', soup.text
    )
    valid_emails = [
        e
        for e in raw_emails
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
    found_emails.update(valid_emails)

    # 2. Jos etusivulta ei löydy, etsitään "Yhteystiedot"-alasivu
    if not found_emails:
      for a in soup.find_all('a', href=True):
        href = a['href'].lower()
        if any(
            w in href for w in ['yhteys', 'contact', 'ota-yhteytta', 'about']
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
                r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+',
                sub_soup.text,
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
              break
          except:
            pass

    # Tallennetaan tulokset
    if found_emails:
      for email in found_emails:
        print(f'  -> Löytyi sähköposti: {email}')
        all_results.append(
            {'Hakusana': HAKUSANA, 'Sivusto': url, 'Sahkoposti': email}
        )
    else:
      print('  -> Sähköpostia ei löytynyt automaattisesti.')
      all_results.append(
          {
              'Hakusana': HAKUSANA,
              'Sivusto': url,
              'Sahkoposti': 'Ei löytynyt',
          }
      )

  except Exception as e:
    print(f'  -> Virhe sivuston käsittelyssä: {e}')

  print('-' * 40)

# Tallennetaan kaikki tulokset CSV-tiedostoon
with open('loytyneet_yritykset.csv', 'w', newline='', encoding='utf-8') as f:
  writer = csv.DictWriter(f, fieldnames=['Hakusana', 'Sivusto', 'Sahkoposti'])
  writer.writeheader()
  writer.writerows(all_results)

print(
    '\nValmista! Tulokset tallennettu tiedostoon: loytyneet_yritykset.csv'
)
