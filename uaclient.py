#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Programa cliente que abre un socket a un servidor
"""

import socket
import sys
import uaserver
from xml.sax import make_parser
from xml.sax.handler import ContentHandler

# Cliente UDP simple.

try:
    config = sys.argv[1]
    method = sys.argv[2]
    option = sys.argv[3]   
except IndexError:
    sys.exit("Usage: python3 uaclient.py config method option")

# Creamos el parser para manejar el fichero xml y recoger los datos del UA

parser = make_parser()
Data_Handler = uaserver.XML_Data_Handler()
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
Log_Path = diccionario_datos["ualog_Path"]
audio_path = diccionario_datos["audio_Path"]

# Creamos el socket, lo configuramos y lo atamos a un servidor/puerto

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as my_socket:
    my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    my_socket.connect((Proxy_IP, int(Proxy_Port)))

    if str.upper(method) == "REGISTER" :

        LINE = str.upper(method) + " sip:" + UA_Name + ":" + Server_Port + " SIP/2.0 \r\n\r\n"
        print("\r\n--Enviando--\r\n" + LINE + "\r\n")
        my_socket.send(bytes(LINE, 'utf-8'))
        data = my_socket.recv(1024)
        message = data.decode('utf-8')
        lista = (message.split())
        print("--Recibido--\r\n" + message + "\r\n")
        if lista == ['SIP/2.0', '100', 'Trying', 'SIP/2.0', '180',
                     'Ringing', 'SIP/2.0', '200', 'OK']:
            LINE = ("ACK sip:" + sys.argv[2][:sys.argv[2].rfind(":")] + " SIP/2.0")
            print("Enviando: " + LINE)
            my_socket.send(bytes(LINE, 'utf-8') + b'\r\n\r\n')
            data = my_socket.recv(1024)

        print("Terminando socket...")

print("Fin.")
