import json
import random
import socket
import sys
import threading
from AA_Player import Modulo
from pymongo import MongoClient   
import pymongo
from kafka import KafkaConsumer
from json import loads

VACIO = '*'
TAM_CIUDAD = 10
MIN_ALIMENTOS = 15
MAX_ALIMENTOS = 25
MAX_MINAS = 25
MIN_MINAS = 15
NUM_CITIES = 4
MIN_CLIMA = -10
MAX_CLIMA = 10

colors = [(85, 72, 98),(124, 180, 184),(78, 108, 80),(158, 118, 118)]

def colored_background(r, g, b, text):
    return f'\033[48;2;{r};{g};{b}m{text}\033[0m'

class Player:
    def __init__(self,alias,posX,posY,nivel):
        self.alias = alias
        self.posX = posX
        self.posY = posY
        self.nivel = nivel
        self.EF = random.randint(MIN_CLIMA,MAX_CLIMA)
        self.EC = random.randint(MIN_CLIMA,MAX_CLIMA)

class Ciudad:
    def __init__(self,nombre,temperatura,tam, num):
        self.casillas = [ [ 0 for i in range(TAM_CIUDAD) ] for j in range(TAM_CIUDAD) ]
        self.nombre = nombre
        self.temperatura = temperatura
        self.alimentos = random.randint(MIN_ALIMENTOS,MAX_ALIMENTOS)
        self.minas = random.randint(MIN_MINAS,MAX_MINAS)
        self.tam = tam

        self.rgb = colors[int(num)]

    def getNombre(self):
        return self.nombre

    def str(self, i):

        c = ''

        for j in range(TAM_CIUDAD):
            r, g, b = self.rgb
            c+=colored_background(r,g,b,' ')#str(self.casillas[i][j])
            c+=colored_background(r,g,b,'  ')

        return c

class Mapa:

    def __init__(self):
        self.ciudades = [ [ 0 for i in range(NUM_CITIES//2) ] for j in range(NUM_CITIES//2) ]
        
    def addCiudad(self,i,j,ciudad):
        self.ciudades[i][j] = ciudad

    def __str__(self):

        ## ---  Nombre dos primeras ciudades ---
        c = '       '
        c += self.ciudades[0][0].getNombre()
        c+=('                     ')
        c += self.ciudades[0][1].getNombre()
        ## ---------------------------------------

        ## -------   Número columnas        -----
        c += '\n       '
        for i in range(21):
            if i == 0:
                continue
            c += str(i)
            if i < 10:
                c +='  '
            else: 
                c+=' '
        ## ---------------------------------------

        c += '\n'
        c += '    '

        ## ---------  Pared superior   -----------
        for i in range(21):
            c += '#  '
        c += '\n'

        ## ---------------------------------------


        ## --------- Casillas ciudades -----------

        num_fila = 0

        for fil in range(TAM_CIUDAD):

            c+= str(num_fila+1)
            if num_fila+1 < 10:
                c +=' '
            c += '  # '

            for i in (0,1):
                c+= self.ciudades[0][i].str(fil)
            c+='\n'

            num_fila+=1

        for fil in range(TAM_CIUDAD):
            c+= str(num_fila+1)

            c += '  # '

            for i in (0,1):
                c+= self.ciudades[1][i].str(fil)
            c+='\n'

            num_fila+=1

        ## ---------------------------------------

        ## ---   Nombre dos últimas ciudades   ---
                 
        c += '       '
        c += self.ciudades[1][0].getNombre()
        c+=('                       ')
        c += self.ciudades[1][1].getNombre()

        ## ----------------------------------------

        return c

def sendWeather(AA_Weather):

    cities = []

    try:
        conn = socket.socket()
    except socket.error as err:
        print('Socket error because of %s' %(err))

    try:
        conn.connect((AA_Weather.getIp(), AA_Weather.getPort()))

        i = 0

        # enviar peticiones hasta que tengamos NUM_CITIES distintas recibidas de AA_Weather
        while i < NUM_CITIES:
            conn.send('send city'.encode())
            city = conn.recv(1024).decode()
            print(f'City received -> {city}')

            if json.loads(city) not in cities:
                cities.append(json.loads(city))
                i += 1
        
        conn.send('ok'.encode())
       
       
    except socket.gaierror:
        print('There an error resolving the host')
        sys.exit() 
                
    conn.close()

    #return cities
    return array2json(cities)

# Construye una lista de keys:value a una lista json
def array2json(array):

    c = { 'ciudades': 
            [
                {
                    'nombre' : array[0]['nombre'],
                    'temperatura' : array[0]['temperatura']
                },
                {
                    'nombre' : array[1]['nombre'],
                    'temperatura' : array[1]['temperatura']
                },
                {
                    'nombre' : array[2]['nombre'],
                    'temperatura' : array[2]['temperatura']
                },
                {
                    'nombre' : array[3]['nombre'],
                    'temperatura' : array[3]['temperatura']
                }
            ]
        }

    return c

# Busca si el jugador con el alias y password existe en nuestra base de datos
def findPlayer(collection,data):

    try:
        result = collection.find_one(data)
        # Si no encuentra ninguno devuelve None
        if result == None:
            return False

    except pymongo.errors.PyMongoError as e:
        print(e)
        return False

    return True

def autentificarJugador(player):

    player.send("Login with your alias and password:".encode())
    login = player.recv(1024).decode()
    dataJson = json.loads(login)

    try:
        conn = MongoClient()
        print("Connected to MongoDB successfully!!!")
    except:  
        print("Could not connect to MongoDB")
        return False

    db = conn.gameDB
    collection = db.players

    if findPlayer(collection,dataJson):
        return True
    
    return False

def escucharMovimientos(Broker):
    consumer = KafkaConsumer(
    'player_move',
     bootstrap_servers=[f'{Broker.getIp()}:{Broker.getPort()}'],
     auto_offset_reset='earliest',
     enable_auto_commit=True,
     group_id='my-group',
     value_deserializer=lambda x: loads(x.decode('utf-8')))

    for message in consumer:
        message = message.value
        print('{} moved registered '.format(message))
    

def handle_player(conn,addr,AA_Broker):

    print("Connection from: " + str(addr))

    if autentificarJugador(conn):
        data = {    'msg' : 'Conectando a partida...',
                    'verified' : True
                }
        data = json.dumps(data)
        conn.send(data.encode())

        escucharMovimientos(AA_Broker)

    else:
        data = {    'msg' : 'Alias o password incorrecto !',
                    'verified' : False
                }
        data = json.dumps(data)
        conn.send(data.encode())

    conn.close()

def conexion_player():
    ## Conexión AA_Player

    AA_Engine = Modulo('AA_Engine')
    Broker = Modulo('Broker')
    engine_socket = socket.socket() 
    engine_socket.bind((AA_Engine.getIp(), AA_Engine.getPort()))  

    engine_socket.listen()

    while True:
        conn, addr = engine_socket.accept()  

        thread = threading.Thread(target=handle_player, args = (conn,addr,Broker))
        thread.start()

        print(f"[ACTIVE CONNECTIONS] {threading.activeCount() - 1}")


def conexion_clima():
    ## Conexión AA_Weather

    mapa = Mapa()
    cities = ''

    #guardar el puerto e IP de weather
    AA_Weather = Modulo('AA_Weather')

    cities = sendWeather(AA_Weather)

    num_bloque = 0
    #lee las ciudades almacenadas en el fichero y las añade al mapa
    for ciudad in cities['ciudades']:

        nueva_ciudad=Ciudad(ciudad['nombre'],ciudad['temperatura'],TAM_CIUDAD,str(num_bloque))

        # i y j tomarán los valores en binario con longitud de dos bits de num_bloque (00,01,10,11)
        i = int(f'{num_bloque:02b}'[0])
        j = int(f'{num_bloque:02b}'[1])
        
        mapa.addCiudad(i,j,nueva_ciudad)
        num_bloque += 1

    print(mapa)

def main():

    ##mostrar menu de partida

    ##esperar conexiones de jugadores
    ##al arrancar la partida manualmente
    conexion_clima()
    conexion_player()
    ##
    conexion_player()


if __name__ == "__main__":
    main()

    