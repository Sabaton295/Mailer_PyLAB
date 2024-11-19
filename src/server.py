from email.mime.text import MIMEText
import configparser
import smtplib
import socket
import random

config = configparser.ConfigParser()
config.read('config.ini')


EMAIL_LOGIN = config['EMAIL']['EMAIL_LOGIN']
EMAIL_PASSWORD = config['EMAIL']['EMAIL_PASSWORD']
SMTP_HOST = config['EMAIL']['SMTP_HOST']
SMTP_PORT = int(config['EMAIL']['SMTP_PORT'])


def send_email(to_email, subject, message):
    msg = MIMEText(message)
    msg['Subject'] = subject
    msg['From'] = EMAIL_LOGIN
    msg['To'] = to_email

    try:
        with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as server:
            server.login(EMAIL_LOGIN, EMAIL_PASSWORD)
            server.send_message(msg)
        return True
    except Exception as e:
        print(f"Ошибка при отправке email: {e}")
        return False


def handle_client(client_socket):
    data = client_socket.recv(1024).decode()
    email, message = data.split('|')

    if not email or not message:
        client_socket.send("Ошибка: Некорректные данные".encode())
        client_socket.close()
        return

    ticket_id = random.randint(10000, 99999)
    subject = f"[Ticket #{ticket_id}] Mailer"

    if send_email(email, subject, message) and send_email(EMAIL_LOGIN, subject, message):
        client_socket.send("OK".encode())
    else:
        client_socket.send("Ошибка: Не удалось отправить email".encode())

    client_socket.close()


def server_start():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('localhost', 8888))
    server.listen(5)

    print("Сервер запущен и ожидает подключений...")

    while True:
        client, addr = server.accept()
        print(f"Подключение от {addr}")
        handle_client(client)


server_start()