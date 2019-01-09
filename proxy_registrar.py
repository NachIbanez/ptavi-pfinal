#!/usr/bin/python3
# -*- coding: utf-8 -*-

import socketserver
import sys
import time
import json
import uaserver
from xml.sax import make_parser
from xml.sax.handler import ContentHandler


class SIPRegisterHandler(socketserver.DatagramRequestHandler):

    diccionario_registro = {}

    def register2json(self):
        """
        Comprueba si algún usuario del registro ha expirado
        y lo borra, y después convierte nuestro registro, que es un
        diccionario, en un fichero JSON
        """
        usuarios = list(self.diccionario_registro)
        for usuario in usuarios:
            gmt_expires = self.diccionario_registro[usuario][1]
            gmt_actual = (time.strftime(' GMT %Y-%m-%d %H:%M:%S',
                          time.gmtime(time.time())))
            if gmt_expires < gmt_actual:
                del self.diccionario_registro[usuario]
        with open("database.json", "w") as json_file:
            json.dump(self.diccionario_registro, json_file, indent=4)

    def json2registered(self):
        """
        Comprueba que haya un fichero llamado registeed.json
        en nuestro directorio, y si existe, mete su contenido
        de los usuario registrados en un diccionario
        """
        try:
            with open("registered.json", "r") as json_file:
                self.diccionario_registro = json.load(json_file)
        except FileNotFoundError:
            pass

    def handle(self):
        """
        Maneja los mensajes que le llegan desde el cliente,
        segun sea REGISTER o Expires la primera palabra que
        encuentre en la línea, o incluye el usuario en el
        diccionario o le mete el valor expires, y si éste es 0,
        lo elimina del diccionario
        """
        self.json2registered()
        line_decoded = "-->"
        for line in self.rfile:
            line_decoded += line.decode('utf-8')
        if "REGISTER" in line_decoded and "Authorizathion:" in line_decoded:
            direccion_sip = line_decoded[line_decoded.find(" "):
                                         line_decoded.find("Expires")]
            self.diccionario_registro[direccion_sip] = \
                [self.client_address[0]]
            Password = line_decoded[line_decoded.rfind(" "):]
            print("-------" + Password + direccion_sip)
            username = direccion_sip[direccion_sip.find(":")+1:direccion_sip.rfind(":")]
            passwd_fich = open("passwords", "a")
            passwd_fich.write("---Username: " + username \
                              + " ---> Password: " + Password + "\n")
            passwd_fich.close()
            self.wfile.write(b'SIP/2.0 200 OK\r\n\r\n')
            self.host, self.port = self.client_address[:2]
            print("Recibido --> " + line.decode('utf-8'), end=" ")
            print("Desde ip:puerto --> " + str(self.host) +
                  ":" + str(self.port), "\n")
            index_expires = line_decoded.find("Expires:")
            expires_line = line_decoded[index_expires:]
            expires = expires_line[expires_line.find(" ")+1:expires_line.find("A")]
            gmt_expires = time.strftime(" GMT %Y-%m-%d %H:%M:%S",
                                        time.gmtime(time.time()
                                                    + int(expires)))
            self.diccionario_registro[direccion_sip].append(gmt_expires)
            if int(expires) == 0:
                del self.diccionario_registro[direccion_sip]
            self.register2json()
        elif "REGISTER" in line_decoded:
            self.wfile.write(b'SIP/2.0 401 Unauthorized\r\nWWW Authenticate: Digest nonce="987987987987987987"')
        elif "INVITE" in line_decoded:
            pass
        print(line_decoded)

if __name__ == "__main__":
    try:
        config = sys.argv[1]
    except Index_Error:
        sys.exit("Usage: python3 proxy_registrar.py config")

    # Creamos el parser para manejar el fichero xml y recoger los datos del UA

    parser = make_parser()
    Data_Handler = uaserver.XML_Data_Handler()
    parser.setContentHandler(Data_Handler)
    parser.parse(open(config))
    diccionario_datos = Data_Handler.dicc_atributos()

    # Pasamos los datos relevantes del XML a variables del programa 

    Server_Name = diccionario_datos["Server_Name"]
    Server_Port = diccionario_datos["Server_Port"]
    Database_Path = diccionario_datos["Database_Path"]
    Passwords_Path = diccionario_datos["Passwords_Path"]
    Log_Path = diccionario_datos["log_Path"]

    serv = socketserver.UDPServer(('', int(Server_Port)), SIPRegisterHandler)
    print("-SERVER ON-PORT " + Server_Port + "\r\n")
    try:
        serv.serve_forever()
    except KeyboardInterrupt:
        print("-SERVER OFF-")
