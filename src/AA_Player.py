from base64 import encode
import socket
import sys
import json
import threading
from kafka import KafkaProducer
from kafka import KafkaConsumer
from classes import Modulo
from time import sleep
from json import dumps
from json import loads
from AA_Engine import Mapa
from AA_Engine import Ciudad
from threading import Thread

alias = ''
password = ''
numJugador = ''
jugadorVivo = True
partidaIniciada = False

def leerMapa(Broker):
    global jugadorVivo
    global partidaIniciada

    grupo = 'my-group_' + numJugador

    consumer = KafkaConsumer(
    'mapa',
     bootstrap_servers=[f'{Broker.getIp()}:{Broker.getPort()}'],
     auto_offset_reset='latest',
     enable_auto_commit=True,
     group_id=grupo,
     value_deserializer=lambda x: loads(x.decode('utf-8')))


##    consumer.poll() ## dummy poll
    ##Ignoramos todos los mensajes que hayan llegado mientras el jugador estaba muerto
##    consumer.seek_to_end()

    for message in consumer:
##        if(partidaIniciada):
            message = message.value

            if('mapa' in message):
                mapa = message['mapa']
                print(mapa)
                print('Choose your direction (N,S,E,W, NE, NW, SE, SW): ')
            elif ('finPartida' in message):
                if (message['finPartida']):
                    consumer.close()
                    return
            else:
                print('MENSAJE ERRONEO')
                consumer.close()
                return

def insertarMovimiento(Broker):
    global jugadorVivo
    global partidaIniciada
    producer = KafkaProducer(bootstrap_servers=[f'{Broker.getIp()}:{Broker.getPort()}'],
                         value_serializer=lambda x: 
                         dumps(x).encode('utf-8'))

    while True:
        data = {'alias': alias,
                'move' : input()}       
        if(jugadorVivo and partidaIniciada):        
            producer.send('player_move', value=data)
        sleep(1)

        if(not(jugadorVivo)):
            producer.close()
            return

def leerEstado(Broker):

    global jugadorVivo
    global partidaIniciada
    grupo = 'my-group_' + numJugador

    consumer = KafkaConsumer(
    'estadoJugador',
     bootstrap_servers=[f'{Broker.getIp()}:{Broker.getPort()}'],
     auto_offset_reset='latest',
     enable_auto_commit=True,
     group_id=grupo,
     value_deserializer=lambda x: loads(x.decode('utf-8')))

##   consumer.poll() ## dummy poll
    ##Ignoramos todos los mensajes que hayan llegado mientras el jugador estaba muerto
##    consumer.seek_to_end()

    for message in consumer:
        message = message.value 
        print(message)

        if(message['alias'] == alias):
            if(message['nivelReal'] == -99):
                print('HAS MUERTO')
                jugadorVivo = False
        if (message['alias'] == 'broadcast'):
            if (message['estadoPartida'] == 'inicioPartida'):
                print('LA PARTIDA HA COMENZADO')
                partidaIniciada = True
            elif (message['estadoPartida'] == 'finPartida'):
                if(jugadorVivo):
                    print('ENHORABUENA. HAS GANADO LA PARTIDA. PULSE CUALQUIER TECLA PARA SALIR')
                    jugadorVivo = False
                    consumer.close()
                else:
                    print('HAS MUERTO. PULSE CUALQUIER TECLA PARA SALIR')
                    jugadorVivo = False
                    consumer.close()
                    return
            else:
                print('MENSAJE BROADCAST INCORRECTO')
                consumer.close()
                return
                
        if(not(jugadorVivo)):
            consumer.close()
            return               

def jugarPartida(Broker):

    t1 = threading.Thread(target=insertarMovimiento, args = [Broker])
    t2 = threading.Thread(target=leerMapa, args = [Broker])
    t3 = threading.Thread(target=leerEstado, args = [Broker])
    t1.start()
    t2.start()
    t3.start()
    t1.join()
    t2.join()
    t3.join()


# El jugador intentará identificarse en la base de datos y si todo es correcto, podrá jugar la partida
def conectarPartida(Broker, AA_Engine):

    global numJugador

    engine_socket = socket.socket()
    engine_socket.connect((AA_Engine.getIp(),AA_Engine.getPort()))

    msg = engine_socket.recv(1024).decode() 
    print(msg)

    global alias
    alias = input('alias: ')
    password = input('password: ')

    login = {   'alias' : alias,
                'password' : password
            }

    login = json.dumps(login)

    engine_socket.send(login.encode())

    data = engine_socket.recv(1024).decode()
    data = json.loads(data)

    print(data['msg'])
    print()

    if data['verified']:
        numJugador = data['numJugador']
        jugarPartida(Broker)

    engine_socket.close()

    return

def insertRegistry(AA_Registry):

    global alias
    alias = input('alias: ')
    password = input('password: ')

    # Se pedirá al usuario el alias y contraseña
    datos = {   "alias":    alias, 
                "password": password,
                "nivel":    '1',
                "posX":     '0',
                "posY":     '0',
                "ef":       '0',
                "ec":       '0',
                "ciudad":   '0'
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
    global alias
    alias = input('alias: ')
    password = input('password: ')

    data = {   'alias' : alias,
                'password' : password
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

    while jugadorVivo:
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