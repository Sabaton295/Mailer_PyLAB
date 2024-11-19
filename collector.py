import imaplib
import email
import time
import configparser

config = configparser.ConfigParser()
config.read('config.ini')

EMAIL_LOGIN = config['EMAIL']['EMAIL_LOGIN']
EMAIL_PASSWORD = config['EMAIL']['EMAIL_PASSWORD']
IMAP_HOST = config['EMAIL']['IMAP_HOST']
IMAP_PORT = int(config['EMAIL']['IMAP_PORT'])
PERIOD_CHECK = int(config['EMAIL']['PERIOD_CHECK'])

def process_email():
    try:
        mail = imaplib.IMAP4_SSL(IMAP_HOST, IMAP_PORT)
        mail.login(EMAIL_LOGIN, EMAIL_PASSWORD)
        mail.select('inbox')

        _, data = mail.search(None, 'ALL')
        mail_ids = data[0].split()

        for i in mail_ids[::-1]:
            _, data = mail.fetch(i, '(RFC822)')
            raw_email = data[0][1]
            msg = email.message_from_bytes(raw_email)

            subject = msg['Subject']
            if "[Ticket #" in subject and "] Mailer" in subject:
                ticket_id = subject.split("#")[1].split("]")[0]
                body = ""
                if msg.is_multipart():
                    for part in msg.walk():
                        ctype = part.get_content_type()
                        cdispo = str(part.get('Content-Disposition'))
                        if ctype == 'text/plain' and 'attachment' not in cdispo:
                            body = part.get_payload(decode=True).decode()
                            break
                else:
                    body = msg.get_payload(decode=True).decode()

                with open('success_request.log', 'a') as f:
                    f.write(f"Ticket ID: {ticket_id}, Message: {body}\n")
            else:
                body = ""
                if msg.is_multipart():
                    for part in msg.walk():
                        ctype = part.get_content_type()
                        cdispo = str(part.get('Content-Disposition'))
                        if ctype == 'text/plain' and 'attachment' not in cdispo:
                            body = part.get_payload(decode=True).decode()
                            break
                else:
                    body = msg.get_payload(decode=True).decode()

                with open('error_request.log', 'a') as f:
                    f.write(f"Error Message: {body}\n")

            mail.store(i, '+FLAGS', '\\Deleted')
        mail.expunge()
        mail.close()
        mail.logout()
    except Exception as e:
        print(f"Ошибка при обработке почты: {e}")

def main():
    while True:
        process_email()
        time.sleep(PERIOD_CHECK)

if __name__ == "__main__":
    main()

