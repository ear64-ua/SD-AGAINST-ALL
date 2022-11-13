from base64 import encode
import socket
import sys
import json
import threading
from kafka import KafkaProducer
from kafka import KafkaConsumer
from time import sleep
from json import dumps
from json import loads
from threading import Thread

alias = ''
password = ''
codigoPartida = 0
jugadorVivo = True
partidaIniciada = False
numMovimientos = 1
ackRecibido = True

class Modulo:
    
    def __init__(self,id):
        self.ip = "127.0.0.1"
        file = open('json_files/addresses.json')
        data = json.load(file)
        file.close()

        for dir in data['direcciones']:
            if dir['Id'] == id:
                self.port = int(dir['port'])

    def setIPfromJson(self,id):
        file = open('json_files/addresses.json')
        data = json.load(file)
        file.close()

        for dir in data['direcciones']:
            if dir['Id'] == id:
                self.ip = dir['IP']

    def setIp(self,ip):
        self.ip = ip
    
    def setPort(self,port):
        self.port = port
    
    def getIp(self):
        return self.ip
    
    def getPort(self):
        return self.port

def leerMapa(Broker):
    global jugadorVivo

    consumer = KafkaConsumer(
    'mapa',
     bootstrap_servers=[f'{Broker.getIp()}:{Broker.getPort()}'],
     auto_offset_reset='latest',
     enable_auto_commit=True,
     value_deserializer=lambda x: loads(x.decode('utf-8')))

    for message in consumer:
            if(jugadorVivo):
                message = message.value
                if(message['codigoPartida']) == codigoPartida:
                    if('mapa' in message):
                        mapa = message['mapa']
                        print(mapa)
                        print('Elige tu movimiento (N, S, E, W, NE, NW, SE, SW): ')
                    elif ('finPartida' in message):
                        if (message['finPartida']):
                            consumer.close()
                            return
                    else:
                        print('MENSAJE ERRONEO')
                        consumer.close()
                        return  
            else:
                consumer.close()
                return
     

def insertarMovimiento(Broker):
    global jugadorVivo
    global numMovimientos
    global partidaIniciada
    global ackRecibido

    producer = KafkaProducer(bootstrap_servers=[f'{Broker.getIp()}:{Broker.getPort()}'],
                         value_serializer=lambda x: 
                         dumps(x).encode('utf-8'))

    while True:
        data = {'alias': alias,
                'codigoPartida' : codigoPartida,
                'numMovimiento' : numMovimientos,
                'move' : input()}       
        if(jugadorVivo and partidaIniciada):        
            producer.send('player_move', value=data)
            numMovimientos = numMovimientos + 1
            ackRecibido = False    
        sleep(1)
        if(not(ackRecibido)):
            print('EL SERVIDOR SE HA CAIDO. POR FAVOR, ESPERA A LA RECONEXION')
            partidaIniciada = False

        if(not(jugadorVivo)):
            producer.close()
            return

def leerEstado(Broker):

    global jugadorVivo
    global numMovimientos
    global partidaIniciada
    global ackRecibido

    consumer = KafkaConsumer(
    'estadoJugador',
     bootstrap_servers=[f'{Broker.getIp()}:{Broker.getPort()}'],
     auto_offset_reset='latest',
     enable_auto_commit=True,
     value_deserializer=lambda x: loads(x.decode('utf-8')))

    for message in consumer:
        message = message.value 
        if(message['codigoPartida']) == codigoPartida:
            if(message['alias'] == alias and partidaIniciada):
                if 'numMovimiento' in message:
                    if(message['numMovimiento'] == numMovimientos-1):
                        ackRecibido = True
                else:        
                    if(message['nivelReal'] == -99):
                        print('HAS MUERTO. PULSA LA TECLA INTRO PARA SALIR')
                        jugadorVivo = False
                    else:
                        print('[DATOS] ' + str(message['alias']) + ' ' + str(message['avatar']) + ' Nivel: ' + str(message['nivelReal']) + '. Ciudad: ' + str(message['ciudad']) + '. Posicion: [' + str(message['posY'] + 1) + ',' + str(message['posX'] + 1) + ']')   
            if (message['alias'] == 'broadcast'):
                if (message['estadoPartida'] == 'inicioPartida'):
                    #Esto es para que no salga el mensaje cuando se recupera la partida de un error del servidor
                    if(partidaIniciada == False):
                        print('LA PARTIDA HA COMENZADO')
                    partidaIniciada = True
                elif (message['estadoPartida'] == 'continuarPartida'):
                    print('SE HA RECUPERADO LA CONEXIÓN CON EL SERVIDOR. PUEDES SEGUIR JUGANDO')
                    partidaIniciada = True    
                elif (message['estadoPartida'] == 'finPartida'):
                    if(partidaIniciada):
                        if(jugadorVivo):
                            print('ENHORABUENA. HAS GANADO LA PARTIDA. PULSA LA TECLA INTRO PARA SALIR')
                            jugadorVivo = False
                        else:
                            print('HAS MUERTO. PULSA LA TECLA INTRO PARA SALIR')
                            jugadorVivo = False
                elif (message['estadoPartida'] == 'finTiempo'):        
                    print('TIEMPO DE PARTIDA FINALIZADO. PULSA LA TECLA INTRO PARA SALIR')
                    jugadorVivo = False    
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


def chooseAvatar():

  emojis = ['\U0001F479','\U0001F47D','\U0001F916','\U0001F480','\U0001F47E','\U0001F47B','\U0001F920']

  print('Choose your avatar:')

  for emoji in enumerate(emojis):
    print(emoji)

  choice = input('> ')
  return emojis[int(choice)]

# El jugador intentará identificarse en la base de datos y si todo es correcto, podrá jugar la partida
def conectarPartida(AA_Engine):

    global codigoPartida

    conectado = False
    engine_socket = None
    engine_socket = socket.socket()
    # usamos el nombre de host y lo pasamos a IP para que se conecte al socket
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
        codigoPartida = data['codigoPartida']    
        conectado = True

    engine_socket.close()
    return conectado

def insertRegistry(AA_Registry):

    global alias
    alias = input('alias: ')
    password = input('password: ')
    avatar = chooseAvatar()

    # Se pedirá al usuario el alias,avatar y contraseña
    datos = {   "alias":    alias, 
                "password": password,
                "avatar":   avatar,
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
    
    if len(sys.argv[1:]) < 2:
        print('Uso incorrecto de argumentos. Use IP_engine IP_registry')
        return -1
    args = sys.argv[1:]

    # Creamos los módulos para conseguir las direcciones necesarias
    AA_Engine = Modulo('AA_Engine')
    AA_Engine.setIp(args[0])
    AA_Registry = Modulo('AA_Registry')
    AA_Registry.setIp(args[1])
    Broker = Modulo('Broker') 
    Broker.setIPfromJson('Broker')

    while jugadorVivo:
        opcion = menu()

        if opcion == '1': # Creamos un usuario
            insertRegistry(AA_Registry)
        elif opcion == '2': # Editamos la contraseña del usuario
            updateRegistry(AA_Registry)
        elif opcion == '3': # Conexión a partida
            if conectarPartida(AA_Engine):
                jugarPartida(Broker)
        else:
            break

    

if __name__ == "__main__":
    main()