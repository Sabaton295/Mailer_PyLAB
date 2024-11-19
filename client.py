import socket

def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(('localhost', 8888))

    email = input("Введите ваш email: ")
    message = input("Введите текст сообщения: ")

    data = f"{email}|{message}"
    client.send(data.encode())

    response = client.recv(1024).decode()
    print(f"Ответ сервера: {response}")

    client.close()

if __name__ == "__main__":
    main()