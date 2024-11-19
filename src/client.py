import tkinter as tk
import tkinter.messagebox as messagebox
import socket
import threading

def send_email(email, message, status_label):
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(('localhost', 8888))
        data = f"{email}|{message}"
        client.send(data.encode())
        response = client.recv(1024).decode()
        client.close()

        if response == "OK":
            status_label.config(text="Email отправлен успешно!")
            messagebox.showinfo("Успех", "Email отправлен успешно!")
        else:
            status_label.config(text=f"Ошибка: {response}")
            messagebox.showerror("Ошибка", response)
    except Exception as e:
        status_label.config(text=f"Ошибка: {e}")
        messagebox.showerror("Ошибка", str(e))

def on_send_click(email_entry, message_entry, status_label):
    email = email_entry.get()
    message = message_entry.get("1.0", tk.END).strip() # Получаем весь текст из Text widget

    if not email or not message:
        messagebox.showwarning("Предупреждение", "Пожалуйста, заполните все поля.")
        return

    status_label.config(text="Отправка...")

    # Создаем отдельный поток для отправки email
    thread = threading.Thread(target=send_email, args=(email, message, status_label))
    thread.start()

def client_start():
    window = tk.Tk()
    window.title("Mailer")

    email_label = tk.Label(window, text="Email:")
    email_label.grid(row=0, column=0, padx=5, pady=5)

    email_entry = tk.Entry(window)
    email_entry.grid(row=0, column=1, padx=5, pady=5)

    message_label = tk.Label(window, text="Сообщение:")
    message_label.grid(row=1, column=0, padx=5, pady=5)

    message_entry = tk.Text(window)
    message_entry.grid(row=1, column=1, padx=5, pady=5)

    send_button = tk.Button(window, text="Отправить", command=lambda: on_send_click(email_entry, message_entry, status_label))
    send_button.grid(row=2, column=1, padx=5, pady=5)

    status_label = tk.Label(window, text="")
    status_label.grid(row=3, column=0, columnspan=2, pady=5)

    window.mainloop()

client_start()