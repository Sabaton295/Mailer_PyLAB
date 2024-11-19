import asyncio
import imaplib
import email
import time
import configparser
import os

from src.utils import extract_text_from_message

if not os.path.exists('logs'):
    os.makedirs('logs')

config = configparser.ConfigParser()
config.read('config.ini')


EMAIL_LOGIN = config['EMAIL']['EMAIL_LOGIN']
EMAIL_PASSWORD = config['EMAIL']['EMAIL_PASSWORD']
IMAP_HOST = config['EMAIL']['IMAP_HOST']
IMAP_PORT = int(config['EMAIL']['IMAP_PORT'])
PERIOD_CHECK = int(config['EMAIL']['PERIOD_CHECK'])


async def process_email():
    try:
        mail = imaplib.IMAP4_SSL(IMAP_HOST, IMAP_PORT)
        mail.login(EMAIL_LOGIN, EMAIL_PASSWORD)
        mail.select('inbox')

        # Получаем только непрочитанные (UNSEEN) сообщения
        _, data = mail.search(None, 'UNSEEN')
        mail_ids = data[0].split()

        for i in mail_ids:
            _, data = mail.fetch(i, '(RFC822)')
            raw_email = data[0][1]
            msg = email.message_from_bytes(raw_email)

            subject = msg['Subject']
            body = await extract_text_from_message(msg)

            if "[Ticket #" in subject and "] Mailer" in subject:
                ticket_id = subject.split("#")[1].split("]")[0]
                with open('logs/success_request.log', 'a', encoding='utf-8') as f:
                    f.write(f"Ticket ID: {ticket_id}, Message: {body}\n")
            else:
                with open('logs/error_request.log', 'a', encoding='utf-8') as f:
                    f.write(f"Error Message: {body}\n")
            mail.store(i, '+FLAGS', '\\Seen')

        mail.close()
        mail.logout()
    except Exception as e:
        print(f"Ошибка при обработке почты: {e}")


async def collector():
    while True:
        await process_email()  # Добавляем await
        await asyncio.sleep(PERIOD_CHECK)

