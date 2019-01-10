#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Clase (y programa principal) para un servidor de eco en UDP simple
"""

import socketserver
import socket
import sys
import os
import time
from xml.sax import make_parser
from xml.sax.handler import ContentHandler


#Tiempo actual en el formato requerido para dicha práctica
def time_now():
    gmt_actual = (time.strftime('%Y%m%d%H%M%S',
                  time.gmtime(time.time())))
    return gmt_actual

#Funcion que se hará cargo de los mensajes log que se imprimirán en pantalla
# y que se introduciran en nuestro fichero txt de log 

def log(log_file, option, ip, port, text):
    log_msg = ""
    if option == "send":
        log_msg = "Sent to " + str(ip) + ":" + str(port) + " " + text + "\n"
    elif option == "receive":
        log_msg = "Received from " + str(ip) + ":" + str(port) + " " + text \
                  + "\n"
    elif option == "error":
        log_msg = "Error: " + text + "\n"
    print(time_now() + " " + log_msg)
    log_txt = open(log_file, "a")
    log_txt.write(time_now() + " " + log_msg)
    log_txt.close()

class XML_Data_Handler(ContentHandler):
    """
    Manejador que nos permitirá extrae datos del UA del fichero XML,
    al igual que en la práctica 3 con los chistes.
    """

    def __init__(self):
        
        self.attr_dicc = {}

    def startElement(self, name, attrs):
        
        if name == 'account':
            username = attrs.get('username', "")
            passwd = attrs.get('password', "")
            self.attr_dicc['UA_Name'] = username
            self.attr_dicc['UA_Password'] = passwd

        if name == 'server':
            name = attrs.get('name', "")
            port = attrs.get('port', "")
            self.attr_dicc['Server_Name'] = name
            self.attr_dicc['Server_Port'] = port

        if name == 'database':
            path = attrs.get('path', "")
            passwd_path = attrs.get('passwd_path', "")
            self.attr_dicc['Database_Path'] = path
            self.attr_dicc['Passwords_Path'] = passwd_path

        if name == 'uaserver':
            puerto = attrs.get('puerto', "")
            self.attr_dicc['Server_Port'] = puerto

        if name == 'rtpaudio':
            puerto = attrs.get('puerto', "")
            self.attr_dicc['RTP_Port'] = puerto

        if name == 'regproxy':
            ip = attrs.get('ip', "")
            puerto = attrs.get('puerto', "")
            self.attr_dicc['proxy_IP'] = ip
            self.attr_dicc['proxy_Port'] = puerto

        if name == 'log':
            path = attrs.get('path', "")
            self.attr_dicc['log_Path'] = path

        if name == 'audio':
            path = attrs.get('path', "")
            self.attr_dicc['audio_Path'] = path

    def dicc_atributos(self):
        """
        Nos devolverá el diccionario con todos los datos relevantes del fichero XML
        """
        return self.attr_dicc

class EchoHandler(socketserver.DatagramRequestHandler):
    """
    Echo server class
    """

    def handle(self):
        # Escribe dirección y puerto del cliente (de tupla client_address)
        while 1:
            # Leyendo línea a línea lo que nos envía el cliente
            # Se harán diferentes acciones según llegue invite, ack o bye
            line = self.rfile.read()
            line = line.decode('utf-8')
            log("ua2log.txt", "receive", "127.0.0.1", 
                int("5005"), " ".join(line.split()))
            method = line[:line.find(" ")]
            if method == "INVITE":
                print("El cliente nos manda " + line)
                if "@" not in line or ":" not in line:
                    Error = "SIP/2.0 400 Bad Request"
                    log("prlog.txt", "send", "127.0.0.1", 
                        int("5005"), Error)
                    self.wfile.write(b'SIP/2.0 400 Bad Request')
                else:
                    msg = 'SIP/2.0 100 Trying' + 'SIP/2.0 180 Ringing' + 'SIP/2.0 200 OK'      
                    log("prlog.txt", "send", "127.0.0.1", 
                        int("5005"), msg)
                    self.wfile.write(b'SIP/2.0 100 Trying\r\n\r\n'
                                     b'SIP/2.0 180 Ringing\r\n\r\n'
                                     b'SIP/2.0 200 OK\r\n\r\n')
            elif method == "ACK":
                aEjecutar = './mp32rtp -i 127.0.0.1 -p 5003 < ' + "cancion.mp3"
                #os.system(aEjecutar)
            elif line[:line.find(" ")] == "BYE":
                if "@" not in line or ":" not in line:
                    Error = "SIP/2.0 400 Bad Request"
                    log("prlog.txt", "send", "127.0.0.1", 
                        int("5005"), Error)
                    self.wfile.write(b'SIP/2.0 400 Bad Request\r\n\r\n')
                else:
                    log("prlog.txt", "send", "127.0.0.1", 
                        int("5005"), 'SIP/2.0 200 OK')
                    self.wfile.write(b'SIP/2.0 200 OK\r\n')
            elif line and method != "INVITE" and method != "BYE"\
                    and method != "ACK":
                self.wfile.write(b'SIP/2.0 405 Method Not Allowed\r\n\r\n')

            # Si no hay más líneas salimos del bucle infinito
            if not line:
                break


if __name__ == "__main__":
    # Creamos servidor de eco y escuchamos
    try:
        config = sys.argv[1]
    except Index_Error:
        sys.exit("Usage: python3 uaserver.py config")

    # Creamos el parser para manejar el fichero xml y recoger los datos del UA

    parser = make_parser()
    Data_Handler = XML_Data_Handler()
    parser.setContentHandler(Data_Handler)
    parser.parse(open(config))
    diccionario_datos = Data_Handler.dicc_atributos()

    # Pasamos los datos relevantes del XML a variables del programa 

    UA_Name = diccionario_datos["UA_Name"]
    UA_Password = diccionario_datos["UA_Password"]
    Server_Port = diccionario_datos["Server_Port"]
    RTP_Port = diccionario_datos["RTP_Port"]
    Proxy_IP = diccionario_datos["proxy_IP"]
    Proxy_Port = diccionario_datos["proxy_Port"]
    Log_Path = diccionario_datos["log_Path"]
    audio_path = diccionario_datos["audio_Path"]

    serv = socketserver.UDPServer(('', int(Server_Port)), EchoHandler)
    print("Listening")
    serv.serve_forever()
