from base64 import encode
import socket
import sys
import json

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

    engine_socket.close()

    # ... autenticación en Engine
    return

def insertRegistry(AA_Registry):

    datos = {   "alias":     input('alias: '), 
                "password": input('password: '),
                "nivel":    '1',
                "ef":       '0',
                "ec":       '0'
            }
    
    datos = json.dumps(datos)
    
    try:
        conn = socket.socket()
    except socket.error as err:
        print('Socket error because of %s' %(err))

    try:
        conn.connect((AA_Registry.getIp(), AA_Registry.getPort()))

        # send action to server
        conn.send('insert'.encode())
        msg = conn.recv(1024).decode()
        print(msg)

        conn.send(datos.encode())
        msg = conn.recv(1024).decode()
        print(msg)

    except socket.gaierror:
        print('There an error resolving the host')
        sys.exit() 
                
    conn.close()

# Conecta con la base de datos y devuelve si se ha insertado o no
def updateRegistry(AA_Registry):

    # contraseña antigua
    data = {    "alias": input('old alias: '),
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
    
    args = open('src/json_files/addresses.json')
    data = json.load(args)

    AA_Engine = Modulo('AA_Engine')
    AA_Registry = Modulo('AA_Registry')
    Broker = Modulo('Broker') 

    args.close()

    while True:
        opcion = menu()

        if opcion == '1':
            insertRegistry(AA_Registry)
        elif opcion == '2':
            updateRegistry(AA_Registry)
            return
        elif opcion == '3':
            conectarPartida(Broker,AA_Engine)
        else:
            break


    

if __name__ == "__main__":
    main()