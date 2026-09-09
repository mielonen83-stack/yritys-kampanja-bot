import smtplib
from email.message import EmailMessage

# VAROITUS: Älä koskaan laita oikeita salasanoja suoraan koodiin,
# jos teet repositoriosta julkisen! Käytä testaukseen esim. erillistä testitiliä.

EMAIL_ADDRESS = 'oma_lahettaja@gmail.com'
EMAIL_PASSWORD = 'gmail_sovellussalasana'

msg = EmailMessage()
msg['Subject'] = 'Yhteistyötarjous'
msg['From'] = EMAIL_ADDRESS
msg['To'] = 'vastaanottaja@yritys.fi'  # Tähän tulee löydetty osoite
msg.set_content(
    'Hei,\n\nHuomasimme yrityksenne ja haluaisimme tarjota palveluitamme...'
)

# Lähetys (esimerkkinä Gmailin SMTP)
try:
  with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
    smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
    smtp.send_message(msg)
  print('Sähköposti lähetetty onnistuneesti!')
except Exception as e:
  print(f'Lähetys epäonnistui: {e}')
