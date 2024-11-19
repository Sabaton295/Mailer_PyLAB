import imaplib
import email
import time
import configparser
import os

from bs4 import BeautifulSoup

config = configparser.ConfigParser()
config.read('config.ini')

EMAIL_LOGIN = config['EMAIL']['EMAIL_LOGIN']
EMAIL_PASSWORD = config['EMAIL']['EMAIL_PASSWORD']
IMAP_HOST = config['EMAIL']['IMAP_HOST']
IMAP_PORT = int(config['EMAIL']['IMAP_PORT'])
PERIOD_CHECK = int(config['EMAIL']['PERIOD_CHECK'])


def extract_text_from_message(msg):
    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get('Content-Disposition'))
            if content_type == 'text/plain' and 'attachment' not in content_disposition:
                body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                break
            elif content_type == 'text/html' and 'attachment' not in content_disposition:
                html = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                soup = BeautifulSoup(html, 'html.parser')
                body = soup.get_text(separator=' ', strip=True)
                break
    else:
        body = msg.get_payload(decode=True).decode('utf-8', errors='ignore')
    return body



def process_email():
    try:
        mail = imaplib.IMAP4_SSL(IMAP_HOST, IMAP_PORT)
        mail.login(EMAIL_LOGIN, EMAIL_PASSWORD)
        mail.select('inbox')

        _, data = mail.search(None, 'UNSEEN')
        mail_ids = data[0].split()

        for i in mail_ids:
            _, data = mail.fetch(i, '(RFC822)')
            raw_email = data[0][1]
            msg = email.message_from_bytes(raw_email)

            subject = msg['Subject']
            body = extract_text_from_message(msg)

            if "[Ticket #" in subject and "] Mailer" in subject:
                ticket_id = subject.split("#")[1].split("]")[0]
                with open('success_request.log', 'a', encoding='utf-8') as f:
                    f.write(f"Ticket ID: {ticket_id}, Message: {body}\n")
            else:
                with open('error_request.log', 'a', encoding='utf-8') as f:
                    f.write(f"Error Message: {body}\n")

            # Помечаем сообщение как прочитанное
            mail.store(i, '+FLAGS', '\\Seen')

        mail.close()
        mail.logout()
    except Exception as e:
        print(f"Ошибка при обработке почты: {e}")


def main():
    while True:
        process_email()
        time.sleep(PERIOD_CHECK)

main()