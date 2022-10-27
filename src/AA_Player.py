from base64 import encode
import socket
import sys
import json
from kafka import KafkaProducer
from time import sleep
from json import dumps


class Modulo:
    
    def __init__(self,id):

        file = open('src/json_files/addresses.json')
        data = json.load(file)
        file.close()

        for dir in data['direcciones']:
            if dir['Id'] == id:
                self.ip = dir['IP']
                self.port = int(dir['port'])

    def setIp(self,ip):
        self.ip = ip
    
    def setPort(self,port):
        self.port = port
    
    def getIp(self):
        return self.ip
    
    def getPort(self):
        return self.port


def jugarPartida(Broker):

    producer = KafkaProducer(bootstrap_servers=[f'{Broker.getIp()}:{Broker.getPort()}'],
                         value_serializer=lambda x: 
                         dumps(x).encode('utf-8'))

    while True:
        data = {'move' : input('Choose your direction (E,W,S,N): ')}
        producer.send('player_move', value=data)
        sleep(2)


# El jugador intentará identificarse en la base de datos y si todo es correcto, podrá jugar la partida
def conectarPartida(Broker, AA_Engine):

    engine_socket = socket.socket()
    engine_socket.connect((AA_Engine.getIp(),AA_Engine.getPort()))

    msg = engine_socket.recv(1024).decode() 
    print(msg)

    login = {   'alias' : input('Alias: '),
                'password' : input('Password: ')
            }

    login = json.dumps(login)

    engine_socket.send(login.encode())

    data = engine_socket.recv(1024).decode()
    data = json.loads(data)

    print(data['msg'])
    print()

    if data['verified']:
        jugarPartida(Broker)

    engine_socket.close()

    return

def insertRegistry(AA_Registry):

    # Se pedirá al usuario el alias y contraseña
    datos = {   "alias":     input('alias: '), 
                "password": input('password: '),
                "nivel":    '1',
                "posX":     '0',
                "posY":     '0',
                "ef":       '0',
                "ec":       '0'
            }
    # Convertimos datos en un string con formato JSON
    datos = json.dumps(datos)
    
    try:
        conn = socket.socket()
    except socket.error as err:
        print('Socket error because of %s' %(err))

    try:
        conn.connect((AA_Registry.getIp(), AA_Registry.getPort()))

        # notificamos al servidor que se quiere insertar
        conn.send('insert'.encode())
        msg = conn.recv(1024).decode()
        print(msg)

        # mandamos los datos al servidor
        conn.send(datos.encode())
        msg = conn.recv(1024).decode()
        print(msg)
        print()

    except socket.gaierror:
        print('There an error resolving the host')
        sys.exit() 
                
    conn.close()

# Conecta con la base de datos y devuelve si se ha insertado o no
def updateRegistry(AA_Registry):

    # contraseña antigua
    print()
    data = {    "alias": input('alias: '),
                "password": input('password: ')
            }
    # convertimos los datos a json para poder enviarlos al servidor
    oldData = json.dumps(data)

    # nueva contraseña
    data = {    "password": input('new password: ') }
    newData = json.dumps(data)

    try:
        conn = socket.socket()
    except socket.error as err:
        print('Socket error because of %s' %(err))

    try:
        conn.connect((AA_Registry.getIp(), AA_Registry.getPort()))

        # send action to server
        conn.send('update'.encode())
        msg = conn.recv(1024).decode()
        print(msg)

        conn.send(oldData.encode())
        msg = conn.recv(1024).decode() # confirmación de datos antiguos

        conn.send(newData.encode())
        msg = conn.recv(1024).decode() # confirmación de insert
        print(msg)
        print()
       
    except socket.gaierror:
        print('There an error resolving the host')
        sys.exit() 
                
    conn.close()

# Muestra el menú de opciones que tiene el jugador
def menu():

    print('Elige una opción:')
    print('1. Crear perfil')
    print('2. Editar perfil')
    print('3. Unirse a partida')
    print('4 Salir')

    return input('Tu opción: ')

def main():
    
    # Creamos los módulos para conseguir las direcciones necesarias
    AA_Engine = Modulo('AA_Engine')
    AA_Registry = Modulo('AA_Registry')
    Broker = Modulo('Broker') 

    while True:
        opcion = menu()

        if opcion == '1': # Creamos un usuario
            insertRegistry(AA_Registry)
        elif opcion == '2': # Editamos la contraseña del usuario
            updateRegistry(AA_Registry)
        elif opcion == '3': # Conexión a partida
            conectarPartida(Broker,AA_Engine)
        else:
            break

    

if __name__ == "__main__":
    main()