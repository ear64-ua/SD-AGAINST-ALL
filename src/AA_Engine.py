import json
import random
import socket
import sys
import threading
from AA_Player import Modulo
from pymongo import MongoClient   
import pymongo


VACIO = '*'
TAM_CIUDAD = 10
TAM_TABLERO = 20
MIN_ALIMENTOS = 15
MAX_ALIMENTOS = 25
MAX_MINAS = 25
MIN_MINAS = 15
NUM_CITIES = 4


class Ciudad:
    def __init__(self,nombre,temperatura,tam):
        self.nombre = nombre
        self.temperatura = temperatura
        self.alimentos = random.randint(MIN_ALIMENTOS,MAX_ALIMENTOS)
        self.minas = random.randint(MIN_MINAS,MAX_MINAS)
        self.tam = tam

    def getNombre(self):
        return self.nombre

class Mapa:

    def __init__(self, tam):
        self.tam = tam
        self.ciudades = []
        
    def addCiudad(self,ciudad):
        self.ciudades.append(ciudad)

    def __str__(self):

        c = '       '
        c += self.ciudades[0].getNombre()
        c+=('\t\t\t  ')
        c += self.ciudades[1].getNombre()

        c += '\n       '
        for i in range(21):
            if i == 0:
                continue
            c += str(i)
            if i < 10:
                c +='  '
            else: 
                c+=' '

        c += '\n'
        c += '    '

        for i in range(21):
            c += '#  '
        c += '\n'

        num_fila = 0
        columna = 0
        indx = 0

        # recorremos por cada fila, dos ciudades e imprimimos sus valores
        for bloque in range(2):

            for fila in range(10):
                c += str(num_fila+1)
                if num_fila+1 < 10:
                    c +=' '
                c += '  #  '

                # agarramos las dos ciudades
                for ciudad in  self.ciudades[indx:indx+2]:
                    for i in range(10):
                        c += VACIO
                        c += '  '
                 

                num_fila += 1
                
                c += '\n'

            # pasamos a las siguientes ciudades
            indx += 2
                 
        c += '       '
        c += self.ciudades[2].getNombre()
        c+=('\t\t\t  ')
        c += self.ciudades[3].getNombre()

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

def handle_player(conn,addr):

    print("Connection from: " + str(addr))

    if autentificarJugador(conn):
        conn.send("Conectando a partida...".encode())
    else:
        conn.send("Alias o password incorrecto !".encode())

    conn.close()

def main():

    ### Conexión AA_Player

    AA_Engine = Modulo('AA_Engine')
    engine_socket = socket.socket() 
    engine_socket.bind((AA_Engine.getIp(), AA_Engine.getPort()))  

    engine_socket.listen()

    while True:
        conn, addr = engine_socket.accept()  

        thread = threading.Thread(target=handle_player, args = (conn,addr))
        thread.start()

        print(f"[ACTIVE CONNECTIONS] {threading.activeCount() - 1}")

        
    
    ### Conexión AA_Weather

    #mapa = Mapa(TAM_TABLERO)
    #cities = ''

    # guardar el puerto e IP de weather
    #AA_Weather = Modulo('AA_Weather')

    #cities = sendWeather(AA_Weather)

    # lee las ciudades almacenadas en el fichero y las añade al mapa
    #for ciudad in cities['ciudades']:
    #    nueva_ciudad=Ciudad(ciudad['nombre'],ciudad['temperatura'],TAM_CIUDAD)
    #    mapa.addCiudad(nueva_ciudad)
    #    print(ciudad)

    #print(mapa)


if __name__ == "__main__":
    main()

    