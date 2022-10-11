import socket
import sys
import json

class Modulo:
    def __init__(self):
        self.port = 0
        self.ip = 0
    
    def setIp(self,ip):
        self.ip = ip
    
    def setPort(self,port):
        self.port = port
    
    def getIp(self):
        return self.ip
    
    def getPort(self):
        return self.port

def conectarPartida():

    alias = input('Alias: ')
    password = input('Password: ')
    # ... autenticación en Engine
    return

def insertRegistry(AA_Registry):

    datos = {  "alias":     input('alias: '), 
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

def updateRegistry(AA_Registry):

    data = { "alias": input('old alias: '),
                "password": input('old password: ')
    }

    oldData = json.dumps(data)

    data = { "alias": input('new alias: '),
                "password": input('new password: ')
    }

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
        msg = conn.recv(1024).decode()

        conn.send(newData.encode())
        msg = conn.recv(1024).decode()
        print(msg)
       
    except socket.gaierror:
        print('There an error resolving the host')
        sys.exit() 
                
    conn.close()
    

def menu():

    print('Elige una opción:')
    print('1. Crear perfil')
    print('2. Editar perfil')
    print('3. Unirse a partida')

    return input('Tu opción: ')

def main():
    
    args = open('player_args.json')
    data = json.load(args)

    AA_Engine = Modulo()
    AA_Registry = Modulo()
    Manager = Modulo() 

    for addr in data['direcciones']:
        if addr['Id'] == 'AA_Engine':
            AA_Engine.setIp(addr['IP'])
            AA_Engine.setPort(int(addr['port']))

        elif addr['Id'] == 'AA_Registry':
            print(f'Registering in {addr} ')
            AA_Registry.setIp(addr['IP'])
            AA_Registry.setPort(int(addr['port']))

        elif addr['Id'] == 'Manager':
            Manager.setIp(addr['IP'])
            Manager.setPort(int(addr['port']))

    args.close()

    opcion = menu()

    if opcion == '1':
        insertRegistry(AA_Registry)
    elif opcion == '2':
        updateRegistry(AA_Registry)
        return
    elif opcion == '3':
        conectarPartida()


    

if __name__ == "__main__":
    main()