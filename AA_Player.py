import socket
import sys
import json

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
    if len(sys.argv) != 3:
        print('ERROR en argumentos. Uso: IP puerto')
        return

    opcion = menu()

    if opcion == '1':
        enviarRegistry(crearPerfil())
    elif opcion == '2':
        return
    elif opcion == '3':
        conectarPartida()


    

if __name__ == "__main__":
    main()