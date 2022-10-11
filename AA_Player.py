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

def enviarRegistry(datos):
    datos = json.dumps(datos)
    
    try:
        sock = socket.socket()
    except socket.error as err:
        print('Socket error because of %s' %(err))

    port = 1500
    address = socket.gethostname()

    try:
        sock.connect((address, port))
        sock.send(datos.encode())
    except socket.gaierror:

        print('There an error resolving the host')

        sys.exit() 
                
    sock.close()

def editarPerfil():
    # editar perfil de usuario existente
    return

def crearPerfil():

    alias = input('alias: ')
    password = input('password: ')
    nivel = input('nivel: ')
    ef = input('ef: ')
    ec = input('ec: ')

    datos = {  "alias":alias, 
                "password":password,
                "nivel": nivel,
                "ef":ef,
                "ec":ec
            }

    return datos

def menu():

    print('Elige una opción:')
    print('1. Crear perfil')
    print('2. Editar perfil')
    print('3. Unirse a partida')

    return input('Tu opción: ')

def main():

    # argumentos:
    #   IP y puerto del AA_Engine
    #   IP y puerto del Broker/Bootstrap-server del gestor de colas
    #   IP y puerto del AA_Registry  
    
    args = open('player_args.json')
    data = json.load(args)

    AA_Engine = Modulo()
    AA_Registry = Modulo()
    Manager = Modulo() 

    for addr in data['direcciones']:
        if addr['Id'] == 'AA_Engine':
            AA_Engine.setIp(addr['IP'])
            AA_Engine.setPort(addr['port'])

        elif addr['Id'] == 'AA_Registry':
            AA_Registry.setIp(addr['IP'])
            AA_Registry.setPort(addr['port'])

        elif addr['Id'] == 'Manager':
            Manager.setIp(addr['IP'])
            Manager.setPort(addr['port'])

    args.close()

    opcion = menu()

    if opcion == '1':
        enviarRegistry(crearPerfil())
    elif opcion == '2':
        editarPerfil()
        return
    elif opcion == '3':
        conectarPartida()


    

if __name__ == "__main__":
    main()