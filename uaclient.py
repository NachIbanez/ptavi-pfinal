#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Programa cliente que abre un socket a un servidor
"""

import socket
import sys
import uaserver
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
Log_Path = diccionario_datos["log_Path"]
audio_path = diccionario_datos["audio_Path"] 

# Creamos el socket, lo configuramos y lo atamos a un servidor/puerto

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as my_socket:
    my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    my_socket.connect((Proxy_IP, int(Proxy_Port)))

    print("\r\n" + time_now() + " Starting..." + "\n")
    log_txt = open(Log_Path, "a")
    log_txt.write(time_now() + " Starting..." + "\n")
    log_txt.close()

    if str.upper(method) == "REGISTER" :

        LINE = str.upper(method) + " sip:" + UA_Name + "127.0.0.1" + \
               " SIP/2.0\r\n\r\n" + "Expires: " + option
        LINE_log = str.upper(method) + " sip:" + UA_Name + "127.0.0.1" + \
               " SIP/2.0" + "Expires: " + option
        log(Log_Path, "send", Proxy_IP, Proxy_Port, LINE_log)
        my_socket.send(bytes(LINE, 'utf-8'))
        data = my_socket.recv(1024)
        message = data.decode('utf-8')
        log(Log_Path, "receive", Proxy_IP, Proxy_Port, message)
        lista = (message.split())
        if lista[1] == "401":
            log(Log_Path, "error", Proxy_IP, Proxy_Port, message[:message.find("WWW")-2])
            LINE = str.upper(method) + " sip:" + UA_Name + ":" + Server_Port + \
                   " SIP/2.0\r\n\r\n" + "Expires: " + option + "\r\n" + \
                   "Authorizathion: Digest response= " + UA_Password
            LINE_log = str.upper(method) + " sip:" + UA_Name + ":" + Server_Port + \
                   " SIP/2.0 " + "Expires: " + option + \
                   " Authorizathion: Digest response= " + UA_Password
            log(Log_Path, "send", Proxy_IP, Proxy_Port, LINE_log)
            my_socket.send(bytes(LINE, 'utf-8'))
            data = my_socket.recv(1024)
            message = data.decode('utf-8')
            if "200" in message:
                log(Log_Path, "receive", Proxy_IP, Proxy_Port, message[:-4])
        print("Registered Succesfully")

    if str.upper(method) == "INVITE" :

        LINE = str.upper(method) + " sip:" + option + "@127.0.0.1"+ \
               " SIP/2.0\r\n\r\n" + "Content-Type: application/sdp" \
               + "\r\n\r\n" + "v=0\n" \
               + "o=" + UA_Name + " 127.0.0.1\n" + "s=sesion-rtp\n" \
               + "t=0\n" + "m=audio 34543 RTP\r\n"
        LINE_log = str.upper(method) + " sip:" + option + ": SIP/2.0 " + \
                   "Content-Type: application/sdp" + " " + "v=0 " \
                   + "o=" + UA_Name + " 127.0.0.1 " + "s=sesion-rtp " \
                   + "t=0 " + "m=audio 34543 RTP"
        log(Log_Path, "send", Proxy_IP, Proxy_Port, LINE_log)
        my_socket.send(bytes(LINE, 'utf-8'))
        data = my_socket.recv(1024)
        message = data.decode('utf-8')
        log(Log_Path, "receive", Proxy_IP, Proxy_Port, " ".join(message.split()))
        lista = (message.split())
        if lista == ['SIP/2.0', '100', 'Trying', 'SIP/2.0', '180',
                     'Ringing', 'SIP/2.0', '200', 'OK']:
            LINE = ("ACK sip:juanito SIP/2.0")
            log(Log_Path, "send", Proxy_IP, Proxy_Port, LINE)
            my_socket.send(bytes(LINE, 'utf-8') + b'\r\n\r\n')
            data = my_socket.recv(1024)

    if str.upper(method) == "BYE" :

        LINE = str.upper(method) + " sip:" + option + "@127.0.0.1" + \
               " SIP/2.0\r\n\r\n"                  
        LINE_log = str.upper(method) + " sip:" + option + ": SIP/2.0 "
        log(Log_Path, "send", Proxy_IP, Proxy_Port, LINE_log)
        my_socket.send(bytes(LINE, 'utf-8'))
        data = my_socket.recv(1024)
        message = data.decode('utf-8')
        log(Log_Path, "receive", Proxy_IP, Proxy_Port, message)

