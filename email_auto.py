import imaplib
import email
from email.header import decode_header
from flask import Flask, jsonify
from urllib.parse import quote
import os
import re
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

def login():
    username = os.getenv('EMAIL')
    password = os.getenv('PASS')

    imap = imaplib.IMAP4_SSL("imap.gmail.com")
    imap.login(username, password)
    return imap

def formatMessage(message):
    message_text = message.decode().split('------------------------------')[0]
    message_text = re.sub(r'\r?\n', '', message_text)
    message_text = re.sub(r"\(.*?\)", "", message_text)
    patron_emoticones = re.compile("[\U0001F600-\U0001F64F]")
    message_text = patron_emoticones.sub("", message_text)
    patron_espacios = r" +"
    message_text = re.sub(patron_espacios, " ", message_text)
    message_text = message_text.replace('hs', 'horas')
    position = message_text.find(
        "Su Cliente de Mail NO soporta mensajes en formato HTM")
    isHtml = message_text.find("<!DOCTYPE HTML>")
    message_text = message_text[:position]
    message_text = message_text[:isHtml]
    return message_text


def castMiting(message):
    posicion = message.find("(ART)")
    message = message[:posicion]
    message = message.replace('Invitación:', '')
    return message


def isPedidosYa(message):
    message_text = message.decode().split('------------------------------')[0]
    message_text = re.sub(r'\r?\n', '', message_text)
    message_text = re.sub(r"\(.*?\)", "", message_text)
    patron = r"\$(\d+)"
    patron_emoticones = re.compile("[\U0001F600-\U0001F64F]")
    message_text = patron_emoticones.sub("", message_text)
    message_text = re.sub(
        patron, lambda match: match.group(1) + " pesos", message_text)
    patron_espacios = r" +"
    message_text = re.sub(patron_espacios, " ", message_text)
    posicion = message_text.find("Qué los disfrutes!")
    message_text = message_text[:posicion]
    return message_text


def isMeet(message):
    patron = r"Google Calendar"
    if re.search(patron, message):
        return True
    return False

def formatFrom(from_):
    from_ = from_.replace("email@mail.com.ar", "Global Tech")
    return from_

def getMessages():
    imap = login()
    imap.select("INBOX")
    fecha = datetime.now().strftime('%d-%b-%Y')
    status, messages = imap.search(None, f'SINCE {fecha}', 'UNSEEN')
    # status, messages = imap.search(None, 'SINCE 29-Mar-2023', 'UNSEEN')
    cant_messages = len(messages[0].decode().split())
    response = "No hay mensajes nuevos"
    if cant_messages > 0:
        messages = int(messages[0].decode().split()[0])
        try:
            res, message = imap.fetch(str(messages), "(RFC822)")
        except:
            response = "Ha ocurrido un error inesperado."
        for res in message:
            if isinstance(res, tuple):
                # Obtener el contenido
                message = email.message_from_bytes(res[1])
                # decodificar el contenido
                subject = decode_header(message["Subject"])[0][0]
                if isinstance(subject, bytes):
                    # convertir a string
                    subject = subject.decode()
                # de donde viene el correo
                from_ = message.get("From").split()[0]
                # si el correo es html
                if message.is_multipart():
                    # Recorrer las partes del correo
                    for part in message.walk():
                        # Extraer el contenido
                        content_type = part.get_content_type()
                        content_disposition = str(
                            part.get("Content-Disposition"))
                        try:
                            # el cuerpo del correo
                            if from_ == "PedidosYa":
                                body = isPedidosYa(
                                    part.get_payload(decode=True))
                            else:
                                body = formatMessage(
                                    part.get_payload(decode=True))
                        except:
                            pass
                        if content_type == "text/plain" and "attachment" not in content_disposition:
                            # Mostrar el cuerpo del correo
                            response = f'Has recibido un nuevo correo de {from_}, {body}'
                        elif "attachment" in content_disposition:
                            if isMeet(body):
                                response = f'Tienes una nueva reunion de {formatFrom(from_)}, {castMiting(subject)}'
                            else:
                                response = f'Has recibido un nuevo correo de {from_} con archivos adjuntos, {body}'
                            # download attachment
                            # nombre_archivo = part.get_filename()
                            # if nombre_archivo:
                            #     if not os.path.isdir(subject):
                            #         # crear una carpeta para el mensaje
                            #         os.mkdir(subject)
                            #     ruta_archivo = os.path.join(
                            #         subject, nombre_archivo)
                            #     # download attachment and save it
                            #     open(ruta_archivo, "wb").write(
                            #         part.get_payload(decode=True))
                else:
                    # contenido del mensaje
                    content_type = message.get_content_type()
                    # cuerpo del mensaje
                    if from_ == "PedidosYa":
                        body = isPedidosYa(
                            part.get_payload(decode=True))
                    else:
                        body = formatMessage(
                            part.get_payload(decode=True))
                    if content_type == "text/plain":
                        # response = f'Has recibido un nuevo correo de texto {from_}, {body}'
                        response = f'Has recibido un nuevo correo de texto {body}'
                    elif content_type == "text/html":
                        # response = f'Has recibido un correo de {from_}, {body}'
                        response = f'Has recibido un correo html,{body}'

                    # Abrir el html en el navegador
                    # if not os.path.isdir(subject):
                    #     os.mkdir(subject)
                    # nombre_archivo = f"{subject}.html"
                    # ruta_archivo = os.path.join(subject, nombre_archivo)
                    # open(ruta_archivo, "w").write(body)
                    # abrir el navegador
                    # webbrowser.open(ruta_archivo)
    imap.close()
    imap.logout()
    return response


# print(getMessages())
app = Flask(__name__)

@app.route('/')
def hello():
    message = getMessages()
    message = {
        "message": message
    }
    response = jsonify(message)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

if __name__ == '__main__':
    app.run(debug=True)
