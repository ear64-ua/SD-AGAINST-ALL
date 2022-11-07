import json
import random
import socket
import sys
import threading
from classes import Modulo
from pymongo import MongoClient   
import pymongo
from kafka import KafkaConsumer
from kafka import KafkaProducer
from json import loads
from json import dumps
from time import sleep

VACIO = '.'
TAM_CIUDAD = 10
MIN_ALIMENTOS = 15
MAX_ALIMENTOS = 25
MAX_MINAS = 25
MIN_MINAS = 15
NUM_CITIES = 4
MIN_CLIMA = -10
MAX_CLIMA = 10

colors = [(85, 72, 98),(124, 180, 184),(78, 108, 80),(158, 118, 118)]

#lista de jugadores que van a tomar parte en la partida
arrayJugadores = []
arrayNPCs = []
maxJugadores = 2
numJugadores = 0
numNPCs = 0
jugadoresVivos = 0


def colored_background(r, g, b, text):
    return f'\033[48;2;{r};{g};{b}m{text}\033[0m'

class Player:
    def __init__(self,alias,nivel,tipo):
        self.alias = alias
        self.aliasCorto = alias[0].upper()
        self.ciudadX = random.randint(0,(NUM_CITIES/2)-1)
        self.ciudadY = random.randint(0,(NUM_CITIES/2)-1)
        self.posX = random.randint(0,TAM_CIUDAD-1)
        self.posY = random.randint(0,TAM_CIUDAD-1)
        self.nivel = nivel
        self.EF = random.randint(MIN_CLIMA,MAX_CLIMA)
        self.EC = random.randint(MIN_CLIMA,MAX_CLIMA)
        self.nivelReal = nivel
        self.tipo = tipo

    def __str__(self):
        return f"alias: {self.alias}, tipo: {self.tipo}, ciudad: [{self.ciudadX}, {self.ciudadY}], posicion: [{self.posX}, {self.posY}], nivel: {self.nivel}, nivelReal: {self.nivelReal}, frio: {self.EF}, calor: {self.EC}"

    def getNivelReal(self):
        return self.nivelReal

    def incrementarNivel(self):
        self.nivel = int(self.nivel) + 1
        self.nivelReal = int(self.nivelReal) + 1

    def matar(self):
        self.nivel = -99
        self.nivelReal = -99         

    def actualizarNivelReal(self):
        ciudad = mapa.getCiudad(self.ciudadX,self.ciudadY)
        temperatura = int(ciudad.getTemperatura())
        if temperatura >= 25:
            self.nivelReal = int(self.nivel) + int(self.EC)
        elif temperatura <= 10:
            self.nivelReal = int(self.nivel) + int(self.EF)
        else:
            self.nivelReal = int(self.nivel)        
            

class Ciudad:
    def __init__(self,nombre,temperatura,tam, num):
        self.casillas = [ [ '.' for i in range(TAM_CIUDAD) ] for j in range(TAM_CIUDAD) ]
        self.nombre = nombre
        self.temperatura = temperatura
        self.alimentos = random.randint(MIN_ALIMENTOS,MAX_ALIMENTOS)
        self.minas = random.randint(MIN_MINAS,MAX_MINAS)
        self.tam = tam

        self.rgb = colors[int(num)]

    def getNombre(self):
        return self.nombre

    def getCasilla(self,x,y):
        return self.casillas[x][y]

    def setCasilla(self,x,y,valor):
        self.casillas[x][y] = valor      

    def getTemperatura(self):
        return self.temperatura

    def rellenarAlimentos(self):
        comida = int(self.alimentos)
        while(comida > 0):
            x = int(random.randint(0,TAM_CIUDAD - 1))
            y = int(random.randint(0,TAM_CIUDAD - 1))
            if(self.casillas[x][y] == '.'):
                self.casillas[x][y] = 'A'
                comida = comida - 1

    def rellenarMinas(self):   
        minas = int(self.minas)
        while(minas > 0):
            x = int(random.randint(0,TAM_CIUDAD - 1))
            y = int(random.randint(0,TAM_CIUDAD - 1))
            if(self.casillas[x][y] == '.'):
                self.casillas[x][y] = 'M'
                minas = minas - 1 
    
    def crearCiudad(self):
        self.rellenarAlimentos()
        self.rellenarMinas()

    def str(self, i):

        c = ''

        for j in range(TAM_CIUDAD):
            r, g, b = self.rgb
            c+=colored_background(r,g,b,' ')
            c+=colored_background(r,g,b,str(self.casillas[i][j]))
            c+=colored_background(r,g,b,' ')

        return c

class Mapa:

    def __init__(self):
        self.ciudades = [ [ 0 for i in range(NUM_CITIES//2) ] for j in range(NUM_CITIES//2) ]
        self.casillas= [[0 for i in range(TAM_CIUDAD*2)] for j in range(TAM_CIUDAD*2)]
        
    def addCiudad(self,i,j,ciudad):
        self.ciudades[i][j] = ciudad

    def getCiudad(self,x,y):
        return self.ciudades[x][y]

    def borrarJugador(self,jugador):
        ciudad = self.ciudades[jugador.ciudadX][jugador.ciudadY]
        ciudad.casillas[jugador.posX][jugador.posY] = '.'

    def colocarJugador(self,jugador):
        ciudad = self.ciudades[jugador.ciudadX][jugador.ciudadY]
        ciudad.casillas[jugador.posX][jugador.posY] = jugador.aliasCorto

    def analizarChoqueJugador(self,jugador):
        global jugadoresVivos
        data = ''
        ciudad = self.ciudades[jugador.ciudadX][jugador.ciudadY]
        casillaDestino = ciudad.casillas[jugador.posX][jugador.posY]
        print("Casilla Destino = " + casillaDestino)
        if casillaDestino == '.':
            self.colocarJugador(jugador)
        elif casillaDestino == 'A':
            if (jugador.tipo == 'PC'):
                jugador.incrementarNivel()
            self.colocarJugador(jugador)
##            data = generarMensajeEstado(jugador)
        elif casillaDestino == 'M':
            if (jugador.tipo == 'PC'):
                jugador.matar()
                jugadoresVivos = jugadoresVivos -1
                data = generarMensajeEstado(jugador)
                ciudad.casillas[jugador.posX][jugador.posY] = '.'    
            else:
                self.colocarJugador(jugador)            
        elif casillaDestino.isnumeric():
            encontrado = False      
        else:
            encontrado = False
            i = 0
            jugador2 = arrayJugadores[i]
            while not(encontrado) and i < len(arrayJugadores):
                jugador2 = arrayJugadores[i]
                posX = jugador2.posX
                posY = jugador2.posY
                alias = jugador2.aliasCorto
                if ((jugador.posX == posX) and (jugador.posY == posY) and jugador.aliasCorto != alias and jugador2.nivelReal >= -10):
                    encontrado = True
                else:
                    i = i + 1    

            if (encontrado):
                if(jugador.nivelReal > jugador2.nivelReal):
                    jugador2.matar()
                    jugadoresVivos = jugadoresVivos - 1
                    data = generarMensajeEstado(jugador2)
                    print("El jugador 1 gana")
                elif(jugador.nivelReal < jugador2.nivelReal):
                    ##Mato al jugador 1
                    jugador.matar()
                    jugadoresVivos = jugadoresVivos - 1
                    print("El jugador 2 gana")
                    data = generarMensajeEstado(jugador)
                else:
                    print("Empate")

        return data             


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

#mapa del mundo
mapa = Mapa()

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

    return result

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

    jugador = findPlayer(collection,dataJson)

    if jugador!=False:
        return jugador
    
    return False

def moverJugador(player, direccion):

    if direccion == "W":
        player.posY = int(player.posY) - 1
        if player.posY < 0:
            player.posY = 9
            player.ciudadY = abs(int(player.ciudadY)- 1)
    elif direccion == "E":
        player.posY = int(player.posY) + 1
        if player.posY > 9:
            player.posY = 0
            player.ciudadY = (int(player.ciudadY) + 1) % 2
    elif direccion == "S":
        player.posX = int(player.posX) + 1
        if player.posX > 9:
            player.posX = 0
            player.ciudadX = (int(player.ciudadX) + 1) % 2
    elif direccion == "N":
        player.posX = int(player.posX) - 1       
        if player.posX < 0:
            player.posX = 9
            player.ciudadX = abs(int(player.ciudadX)- 1)
    elif direccion == "SW":
        player.posX = int(player.posX) + 1
        player.posY = int(player.posY) - 1
        if player.posY < 0:
            player.posY = 9
            player.ciudadY = abs(int(player.ciudadY) - 1)
        if player.posX > 9:
            player.posX = 0
            player.ciudadX = (int(player.ciudadX) + 1) % 2   
    elif direccion == "NW":
        player.posX = int(player.posX) - 1
        player.posY = int(player.posY) - 1
        if player.posY < 0:
            player.posY = 9
            player.ciudadY = abs(int(player.ciudadY) - 1)
        if player.posX < 0:
            player.posX = 9
            player.ciudadX = abs(int(player.ciudadX)- 1)  
    elif direccion == "SE":
        player.posX = int(player.posX) + 1
        player.posY = int(player.posY) + 1
        if player.posY > 9:
            player.posY = 0
            player.ciudadY = (int(player.ciudadY) + 1) % 2
        if player.posX > 9:
            player.posX = 0
            player.ciudadX = (int(player.ciudadX) + 1) % 2
    elif direccion == "NE":
        player.posX = int(player.posX) - 1
        player.posY = int(player.posY) + 1
        if player.posY > 9:
            player.posY = 0
            player.ciudadY = (int(player.ciudadY) + 1) % 2       
        if player.posX < 0:
            player.posX = 9
            player.ciudadX = abs(int(player.ciudadX)- 1)        
    else:
        return False

    return True

def buscarJugador(array, alias):
    i = 0
    while i < len(array):
        if array[i].alias == alias:
            return array[i]
        else:
            i = i + 1

    return False            

def escucharMovimientos(Broker):

    global jugadoresVivos

    consumer = KafkaConsumer(
    'player_move',
     bootstrap_servers=[f'{Broker.getIp()}:{Broker.getPort()}'],
     auto_offset_reset='latest',
     enable_auto_commit=True,
     group_id='my-group',
     value_deserializer=lambda x: loads(x.decode('utf-8')))

    consumer.poll() ## dummy poll
    ##Ignoramos todos los mensajes que hayan llegado mientras el jugador estaba muerto
    consumer.seek_to_end()

    for message in consumer:
        message = message.value
        print('{} moved registered '.format(message))
        direccion = message['move']
        alias = message['alias']
        jugador = buscarJugador(arrayJugadores, alias)
        if jugador != False:
            if int(jugador.nivelReal) >= -10: ##Caso se mueve un jugador vivo. Si esta muerto, se ignora
                ##quito del mapa al jugador
                mapa.borrarJugador(jugador)
                ##coloco al jugador en su nueva casilla
                moverJugador(jugador,direccion)
                jugador.actualizarNivelReal()
                ##compruebo si hay algo en la nueva casilla y pinto el resultado
                data = mapa.analizarChoqueJugador(jugador)
                
                if data != '':
                    ##Envio el estado de los jugadores implicados en el movimiento
                    enviarEstadoPartida(Broker, data)
                ##Envio el mensaje de final de partida cuando solo queda un jugador vivo    
                if (jugadoresVivos == 1):
                    enviarMensajeBroadcast(Broker, 'finPartida')    
                ##Envio el mapa a los jugadores para que lo pinten tambien
                enviarMapa(Broker)
                if(jugadoresVivos == 1):
                    return

                print(jugador)
                print(mapa)
        else: ##caso se mueve un NPC  
            jugador = buscarJugador(arrayNPCs, alias)
            if (jugador == False): ##El jugador no está presente en el array
                ##Creo un nuevo jugador NPC y lo meto en el array de NPCs
                jugador = Player(alias, int(alias[0]), 'NPC')
                arrayNPCs.append(jugador)
            mapa.borrarJugador(jugador)    
            moverJugador(jugador,direccion)
            data = mapa.analizarChoqueJugador(jugador)
            if data != '':
                ##Envio el estado de los jugadores implicados en el movimiento
                enviarEstadoPartida(Broker, data)
                ##Envio el mensaje de final de partida cuando solo queda un jugador vivo    
                if (jugadoresVivos == 1):
                    enviarMensajeBroadcast(Broker, 'finPartida')    
                ##Envio el mapa a los jugadores para que lo pinten tambien
            enviarMapa(Broker)
            if(jugadoresVivos == 1):
                return

            print(jugador)
            print(mapa)


def enviarMapa(Broker):
    producer = KafkaProducer(bootstrap_servers=[f'{Broker.getIp()}:{Broker.getPort()}'],
                         value_serializer=lambda x: 
                         dumps(x).encode('utf-8'))

    if (jugadoresVivos > 1):
        data = {'mapa' : str(mapa)}
    else:
        data = {'finPartida': True}
    
    producer.send('mapa', value=data)

def generarMensajeEstado(jugador):
    data = {'alias' : jugador.alias,
           'nivelReal' : jugador.nivelReal
    }
    return data    

def enviarEstadoPartida(Broker, data):
    producer = KafkaProducer(bootstrap_servers=[f'{Broker.getIp()}:{Broker.getPort()}'],
                         value_serializer=lambda x: 
                         dumps(x).encode('utf-8'))

    producer.send('estadoJugador', value=data)

##Los mensajes de broadcast pueden ser de inicio o de fin de partida
def enviarMensajeBroadcast(Broker, mensaje):
    producer = KafkaProducer(bootstrap_servers=[f'{Broker.getIp()}:{Broker.getPort()}'],
                         value_serializer=lambda x: 
                         dumps(x).encode('utf-8'))

    data = {'alias' : 'broadcast', 
            'estadoPartida' : mensaje}

    producer.send('estadoJugador', value=data)    

def handle_player(conn,addr):

    print("Connection from: " + str(addr))

    global numJugadores
    jugador = autentificarJugador(conn)

    if jugador != False:
        objetoJugador = Player(jugador['alias'], jugador['nivel'], 'PC')
        arrayJugadores.append(objetoJugador)
        for i in range(len(arrayJugadores)):
            print(arrayJugadores[i])

        data = {    'msg' : 'BIENVENIDO A AGAINST ALL. POR FAVOR, ESPERA A QUE SE CONECTE EL RESTO DE JUGADORES',
                    'verified' : True,
                    'numJugador' : str(numJugadores)
                }
        data = json.dumps(data)
        conn.send(data.encode())
        numJugadores = numJugadores + 1       

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
    engine_socket = socket.socket() 
    engine_socket.bind((AA_Engine.getIp(), AA_Engine.getPort()))  

    engine_socket.listen()

    while numJugadores < maxJugadores:
        conn, addr = engine_socket.accept()  

#        thread = threading.Thread(target=handle_player, args = (conn,addr))
#        thread.start()

        handle_player(conn,addr)

        print(f"[ACTIVE CONNECTIONS] {threading.activeCount() - 1}")

    engine_socket.close()    
    return True

def conexion_clima():
    ## Conexión AA_Weather

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


def colocarJugadores():
    for jugador in arrayJugadores:
        ciudad = mapa.getCiudad(jugador.ciudadX,jugador.ciudadY)
        ciudad.setCasilla(jugador.posX,jugador.posY,jugador.aliasCorto)
        jugador.actualizarNivelReal()    

def rellenarCiudades():
    for i in range(int(NUM_CITIES/2)):
        for j in range(int(NUM_CITIES/2)):
            mapa.ciudades[i][j].crearCiudad()

def comenzarPartida():

    global jugadoresVivos
    jugadoresVivos = numJugadores

    Broker = Modulo('Broker')
    conexion_clima()
    colocarJugadores()
    rellenarCiudades()
    print(mapa)
    enviarMensajeBroadcast(Broker, 'inicioPartida')
    enviarMapa(Broker)
    escucharMovimientos(Broker)

    print("FIN DE LA PARTIDA")    

def main():

    arrayJugadores.clear
    arrayNPCs.clear

    print('ESPERANDO JUGADORES')

    ##Esperamos que los jugadores se conecten
    conexion_player()
    
    sleep(3)
    ##Creamos la partida y empezamos a jugar
    comenzarPartida()

if __name__ == "__main__":
    main()

    