import json
import random
import socket
import sys
import threading
from pymongo import MongoClient   
import pymongo
from kafka import KafkaConsumer
from kafka import KafkaProducer
from json import loads
from json import dumps
from time import sleep
from types import SimpleNamespace

VACIO = '.'
TAM_CIUDAD = 10
MIN_ALIMENTOS = 15
MAX_ALIMENTOS = 25
MAX_MINAS = 25
MIN_MINAS = 15
NUM_CITIES = 4
MIN_CLIMA = -10
MAX_CLIMA = 10

SOCK_CLOSE = ''
ERR_WEATHER = '[SOCKET] Hubo un error al conectar con el servidor de tiempo'
BD_CONNECTION = "[BD] Connected to MongoDB successfully!!!"
BD_ERR = "[BD] Could not connect to MongoDB"
BD_CLOSE = '[BD] Close connection'
UNSAVED_MATCH = "[PARTIDA] No existe una partida guardada. Se procede a crear una partida nueva"
ERR_ARGS = '[ARGS] Uso incorrecto de argumentos. Use IP_engine IP_weather maxJugadores tiempoPartida'
ERR_MATCH = "[PARTIDA] ERROR. LA PARTIDA NO PUEDE COMENZAR"

colors = [(85, 72, 98),(124, 180, 184),(78, 108, 80),(158, 118, 118)]

#lista de jugadores que van a tomar parte en la partida
arrayJugadores = []
arrayNPCs = []
maxJugadores = 3
numJugadores = 0
numNPCs = 0
jugadoresVivos = 0
tiempoPartida = 300
codigoPartida = 0

def colored_background(r, g, b, text):
    return f'\033[48;2;{r};{g};{b}m{text}\033[0m'

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


class Player:
    def __init__(self,alias,nivel,tipo,avatar):
        self.alias = alias
        self.avatar = avatar
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
#        self.casillas= [[0 for i in range(TAM_CIUDAD*2)] for j in range(TAM_CIUDAD*2)]
        
    def addCiudad(self,i,j,ciudad):
        self.ciudades[i][j] = ciudad

    def getCiudad(self,x,y):
        return self.ciudades[x][y]

    def borrarJugador(self,jugador):
        ciudad = self.ciudades[jugador.ciudadX][jugador.ciudadY]
        ciudad.casillas[jugador.posX][jugador.posY] = '.'

    def colocarJugador(self,jugador):
        ciudad = self.ciudades[jugador.ciudadX][jugador.ciudadY]
        ciudad.casillas[jugador.posX][jugador.posY] = jugador.avatar

    def analizarChoqueJugador(self,jugador):
        global jugadoresVivos
        data = ''
        ciudad = self.ciudades[jugador.ciudadX][jugador.ciudadY]
        casillaDestino = ciudad.casillas[jugador.posX][jugador.posY]
        if casillaDestino == '.':
            self.colocarJugador(jugador)
            data = generarMensajeEstado(jugador)
        elif casillaDestino == 'A':
            if (jugador.tipo == 'PC'):
                jugador.incrementarNivel()
            self.colocarJugador(jugador)
            data = generarMensajeEstado(jugador)
        elif casillaDestino == 'M':
            if (jugador.tipo == 'PC'):
                jugador.matar()
                jugadoresVivos = jugadoresVivos -1
                data = generarMensajeEstado(jugador)
                ciudad.casillas[jugador.posX][jugador.posY] = '.'    
            else:
                self.colocarJugador(jugador)            
        else:
            if str(casillaDestino).isnumeric():
                array = arrayNPCs
            else:
                array = arrayJugadores        
            encontrado = False
            i = 0
            jugador2 = array[i]
            while not(encontrado) and i < len(array):
                jugador2 = array[i]
                posX = jugador2.posX
                posY = jugador2.posY
                alias = jugador2.avatar
                if ((jugador.posX == posX) and (jugador.posY == posY) and jugador.avatar != alias and jugador2.nivelReal >= -10):
                    encontrado = True
                else:
                    i = i + 1    

            if (encontrado):
                if(jugador.nivelReal > jugador2.nivelReal):
                    ##Mato al jugador 2
                    jugador2.matar()
                    if jugador2.tipo == 'PC':
                        jugadoresVivos = jugadoresVivos - 1
                    data = generarMensajeEstado(jugador2)
                    ciudad.casillas[jugador.posX][jugador.posY] = jugador.avatar 
                elif(jugador.nivelReal < jugador2.nivelReal):
                    ##Mato al jugador 1
                    jugador.matar()
                    if jugador.tipo == 'PC':
                        jugadoresVivos = jugadoresVivos - 1
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
        print('[SOCKET] Socket error because of %s' %(err))

    try:
        conn.connect((AA_Weather.getIp(), AA_Weather.getPort()))

        i = 0

        # enviar peticiones hasta que tengamos NUM_CITIES distintas recibidas de AA_Weather
        while i < NUM_CITIES:
            conn.send('send city'.encode())
            city = conn.recv(1024).decode()
            print(f'[SOCKET] City received -> {city}')

            if json.loads(city) not in cities:
                cities.append(json.loads(city))
                i += 1
        
        conn.send('ok'.encode())
       
    except: 
        if socket.gaierror:
            print('[SOCKET] There was an error while resolving the host')
        else:
            print(ERR_WEATHER)    
        conn.close()
        return False

                
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
        conn = MongoClient('mongodb://mongodb')
        print(BD_CONNECTION)
    except:  
        print(BD_ERR)
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
     value_deserializer=lambda x: loads(x.decode('utf-8')))

    for message in consumer:
        finTiempo = False
        message = message.value
        
        try:
            direccion = message['move']
            alias = message['alias']
        except:
            finTiempo = message['finTiempo']
        if (message['codigoPartida'] == codigoPartida or message['codigoPartida'] == 'NPC'):
            print('[KAFKA] {}'.format(message))
            if finTiempo:
                return
            jugador = buscarJugador(arrayJugadores, alias)
            if jugador != False:
                if int(jugador.nivelReal) >= -10: ##Caso se mueve un jugador vivo. Si esta muerto, se ignora
                    #Genero el ACK correspondiente al mensaje que acabo de leer
                    data = generarAckMovimiento(jugador, message['numMovimiento'])
                    enviarMensaje(Broker, 'ackMovimiento', data)
                    ##quito del mapa al jugador
                    mapa.borrarJugador(jugador)
                    ##coloco al jugador en su nueva casilla
                    moverJugador(jugador,direccion)
                    jugador.actualizarNivelReal()
                    ##compruebo si hay algo en la nueva casilla y pinto el resultado
                    data = mapa.analizarChoqueJugador(jugador)
                    
                    if data != '':
                        ##Envio el estado del jugador implicado en el movimiento
                        enviarMensaje(Broker, 'estadoJugador', data)
                    ##Envio el mensaje de final de partida cuando solo queda un jugador vivo    
                    if (jugadoresVivos == 1):
                        enviarMensaje(Broker,'broadcast', 'finPartida')    
                    ##Envio el mapa a los jugadores para que lo pinten tambien
                    enviarMensaje(Broker, 'mapa', None)
                    if(jugadoresVivos == 1):
                        return

                    print(jugador)
                    print(mapa)
            else: ##caso se mueve un NPC  
                jugador = buscarJugador(arrayNPCs, alias)
                if (jugador == False): ##El jugador no está presente en el array
                    ##Creo un nuevo jugador NPC y lo meto en el array de NPCs
                    jugador = Player(alias, int(alias[0]), 'NPC',message['nivel'])
                    arrayNPCs.append(jugador)
                mapa.borrarJugador(jugador)    
                moverJugador(jugador,direccion)
                data = mapa.analizarChoqueJugador(jugador)
                if data != '':
                    ##Envio el estado de los jugadores implicados en el movimiento
                    enviarMensaje(Broker,'estadoJugador', data)
                    ##Envio el mensaje de final de partida cuando solo queda un jugador vivo    
                    if (jugadoresVivos == 1):
                        enviarMensaje(Broker, 'broadcast', 'finPartida')    
                    ##Envio el mapa a los jugadores para que lo pinten tambien
                enviarMensaje(Broker, 'mapa', None)
                if(jugadoresVivos == 1):
                    return

                print(jugador)
                print(mapa)

            borrarPartidaGuardada()
            guardarPartida()    


def generarMensajeEstado(jugador):
    ciudad = mapa.ciudades[jugador.ciudadX][jugador.ciudadY]
    data = {'alias' : jugador.alias,
           'nivelReal' : jugador.nivelReal,
           'codigoPartida' : codigoPartida,
            'avatar' : jugador.avatar,
           'ciudad' : ciudad.nombre,
           'posX' : jugador.posX,
           'posY' : jugador.posY
    }
    return data

def generarAckMovimiento(jugador, numMovimiento):
    data = {'alias' : jugador.alias,
           'nivelReal' : jugador.nivelReal,
           'numMovimiento' : numMovimiento,
           'codigoPartida' : codigoPartida
    }
    return data        

def enviarMensaje(Broker, tipoMensaje, valorMensaje):
    producer = KafkaProducer(bootstrap_servers=[f'{Broker.getIp()}:{Broker.getPort()}'],
                         value_serializer=lambda x: 
                         dumps(x).encode('utf-8'))

    cola = ''
    data = ''

    if tipoMensaje == 'broadcast':
        cola = 'estadoJugador'
        data = {'alias' : 'broadcast', 
                'estadoPartida' : valorMensaje,
                'codigoPartida' : codigoPartida}
    elif tipoMensaje == 'estadoJugador':
        cola = 'estadoJugador'
        data = valorMensaje
    elif tipoMensaje == 'ackMovimiento':
        cola = 'estadoJugador'
        data = valorMensaje            
    elif tipoMensaje == 'mapa':
        cola = 'mapa'
        if (jugadoresVivos > 1):
            data = {'mapa' : str(mapa),
                    'codigoPartida' : codigoPartida}
        else:
            data = {'finPartida': True,
                    'codigoPartida' : codigoPartida}
    elif tipoMensaje == 'player_move':
        cola = 'player_move'
        data = {'finTiempo' : True,
                'codigoPartida' : codigoPartida}
    else:
        print('[PARTIDA] ERROR EN FUNCION ENVIARMENSAJE')

    if cola != '':   
        producer.send(cola, value=data)

def finalizarPartidaPorTiempo(Broker):
    
    tiempo = 0

    while tiempo < tiempoPartida:
        sleep(1)
        tiempo = tiempo + 1
        if jugadoresVivos == 1:
            return

    enviarMensaje(Broker,'broadcast', 'finTiempo')
    enviarMensaje(Broker, 'mapa', 'finTiempo')
    enviarMensaje(Broker, 'player_move', 'finTiempo')

    return 

def handle_player(conn,addr):

    print("[SOCKET] Connection from: " + str(addr))

    global numJugadores
    jugador = autentificarJugador(conn)
    if jugador != False:
        objetoJugador = Player(jugador['alias'], jugador['nivel'], 'PC',jugador['avatar'])
        if(buscarJugador(arrayJugadores,jugador['alias'])):
            data = {    'msg' : 'El jugador ya está registrado en la partida',
                        'verified' : False
                }
            data = json.dumps(data)
            conn.send(data.encode())
        else:
            arrayJugadores.append(objetoJugador)
            for i in range(len(arrayJugadores)):
                print(arrayJugadores[i])

            data = {    'msg' : 'BIENVENIDO A AGAINST ALL. POR FAVOR, ESPERA A QUE SE CONECTE EL RESTO DE JUGADORES',
                        'verified' : True,
                        'codigoPartida' : codigoPartida
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
    print("[SOCKET] Closed connection: " + str(addr))

def conexion_player(AA_Engine):
    ## Conexión AA_Player
    threading.current_thread()
    engine_socket = socket.socket() 
    engine_socket.bind((AA_Engine.getIp(), AA_Engine.getPort())) 

    engine_socket.listen()

    while numJugadores < maxJugadores:        
        if (threading.active_count() - 1 < maxJugadores - numJugadores):
            conn, addr = engine_socket.accept()  
            thread = threading.Thread(target=handle_player, args = (conn,addr))
            thread.start()

    engine_socket.close()    
    print('[SOCKET] Closed')
    return True

def conexion_clima(AA_Weather):
    ## Conexión AA_Weather

    cities = ''

    cities = sendWeather(AA_Weather)

    num_bloque = 0
    #lee las ciudades almacenadas en el fichero y las añade al mapa
    
    if cities == False:
        return False
    else:    
        for ciudad in cities['ciudades']:

            nueva_ciudad=Ciudad(ciudad['nombre'],ciudad['temperatura'],TAM_CIUDAD,str(num_bloque))

            # i y j tomarán los valores en binario con longitud de dos bits de num_bloque (00,01,10,11)
            i = int(f'{num_bloque:02b}'[0])
            j = int(f'{num_bloque:02b}'[1])
            
            mapa.addCiudad(i,j,nueva_ciudad)
            num_bloque += 1
        return True    

def colocarJugadores():
    for jugador in arrayJugadores:
        ciudad = mapa.getCiudad(jugador.ciudadX,jugador.ciudadY)
        ciudad.setCasilla(jugador.posX,jugador.posY,jugador.avatar)
        jugador.actualizarNivelReal()    

def rellenarCiudades():
    for i in range(int(NUM_CITIES/2)):
        for j in range(int(NUM_CITIES/2)):
            mapa.ciudades[i][j].crearCiudad()

def cargarCiudad(objeto, coordenada):
    ciudad = json.loads(objeto[coordenada], object_hook=lambda d: SimpleNamespace(**d))
    nuevaCiudad = Ciudad(ciudad.nombre,ciudad.temperatura,ciudad.tam,1)
    nuevaCiudad.alimentos = ciudad.alimentos
    nuevaCiudad.minas = ciudad.minas
    nuevaCiudad.rgb = ciudad.rgb
    nuevaCiudad.casillas = ciudad.casillas

    return nuevaCiudad

def cargarJugador(player):
    jugador = Player(player['alias'], player['nivel'], player['tipo'], player['avatar'])    
    jugador.ciudadX = player['ciudadX']
    jugador.ciudadY = player['ciudadY']
    jugador.posX = player['posX']
    jugador.posY = player['posY']
    jugador.EF = player['EF']
    jugador.EC = player['EC']
    jugador.nivelReal = player['nivelReal']

    return jugador

def cargarPartida():

    global jugadoresVivos, codigoPartida
    
    try:
        conn = MongoClient('mongodb://mongodb')
        print(BD_CONNECTION)
        db = conn.gameDB

        try:
            db.validate_collection('partida')
        except pymongo.errors.OperationFailure:
            print(UNSAVED_MATCH)
            conn.close()
            print(BD_CLOSE)
            return False
    except:  
        print(BD_ERR)
        return False

    try:
        collection = db.partida
        partida = collection.find_one({'codigoPartida' : codigoPartida})
        if (partida == None):
            print(UNSAVED_MATCH)
            conn.close()
            return False
        else: 
            print('[BD] Cargando partida ...')
            nuevaCiudad = cargarCiudad(partida, 'c1')
            mapa.ciudades[0][0] = nuevaCiudad
            nuevaCiudad = cargarCiudad(partida, 'c2')
            mapa.ciudades[0][1] = nuevaCiudad
            nuevaCiudad = cargarCiudad(partida, 'c3')
            mapa.ciudades[1][0] = nuevaCiudad
            nuevaCiudad = cargarCiudad(partida, 'c4')
            mapa.ciudades[1][1] = nuevaCiudad

            print(partida['jugadores'])
            lista = json.loads(partida['jugadores'])

            for player in lista:
                jugador = cargarJugador(player)
                arrayJugadores.append(jugador)

            jugadoresVivos = partida['jugadoresVivos']
            codigoPartida = partida['codigoPartida']     
            conn.close()
            print(BD_CLOSE)
    except:
        print("[BD] Error al cargar la partida")
        conn.close()
        print(BD_CLOSE)

    return True             

def guardarPartida():
    try:
        conn = MongoClient('mongodb://mongodb')
        print(BD_CONNECTION)
    except:  
        print(BD_ERR)
        return False

    db = conn.gameDB
    collection = db.partida
    jugadores = json.dumps([jugador.__dict__ for jugador in arrayJugadores])
    data = {
                'c1' : json.dumps(mapa.ciudades[0][0].__dict__),
                'c2' : json.dumps(mapa.ciudades[0][1].__dict__),
                'c3' : json.dumps(mapa.ciudades[1][0].__dict__),  
                'c4' : json.dumps(mapa.ciudades[1][1].__dict__),
                'jugadores' : jugadores,
                'jugadoresVivos' : jugadoresVivos,
                'codigoPartida' : codigoPartida
           }
    collection.insert_one(data)
    print('[BD] Guardando partida ...')
    conn.close()
    print(BD_CLOSE)

def borrarPartidaGuardada():
    try:
        conn = MongoClient('mongodb://mongodb')
        print(BD_CONNECTION)
    except:  
        print(BD_ERR)
        return False

    db = conn.gameDB

    try:
        db.validate_collection('partida')
        db.partida.delete_one({'codigoPartida' : codigoPartida})
    except pymongo.errors.OperationFailure:
        print("[PARTIDA] No se puede borrar partida ")
        conn.close()
        print(BD_CLOSE)
        return
    print('[BD] Borrando partida ...')                 
    print(BD_CLOSE)
    conn.close()

def generarPartida(AA_Weather):
    global jugadoresVivos
    jugadoresVivos = numJugadores

    if conexion_clima(AA_Weather):
        colocarJugadores()
        rellenarCiudades()
        guardarPartida()
        return True
    else:
        return False    

def comenzarPartida():

    Broker = Modulo('Broker')
    Broker.setIPfromJson('Broker')
    
    print(mapa)
    enviarMensaje(Broker,'broadcast', 'inicioPartida')
    enviarMensaje(Broker, 'mapa', None)
    t1 = threading.Thread(target=escucharMovimientos, args = [Broker])
    t2 = threading.Thread(target=finalizarPartidaPorTiempo, args = [Broker])
    t1.start()
    t2.start()
    t1.join()
    t2.join()

    borrarPartidaGuardada()

    print("FIN DE LA PARTIDA")    


def main():

    global codigoPartida, maxJugadores, tiempoPartida
    comenzar = False

    arrayJugadores.clear
    arrayNPCs.clear

    if len(sys.argv[1:]) < 4:
        print(ERR_ARGS)
        return -1
    args = sys.argv[1:]

    AA_Engine = Modulo('AA_Engine')
    AA_Engine.setIp(args[0])

    AA_Weather = Modulo('AA_Weather')
    AA_Weather.setIp(args[1])

    try:
        maxJugadores = int(args[2])
        tiempoPartida = int(args[3])
    except:
        print(ERR_ARGS)
        return -1;

    codigoPartida = AA_Engine.getIp()
    if(cargarPartida() == True):
        Broker = Modulo('Broker')
        Broker.setIPfromJson('Broker')
        enviarMensaje(Broker, 'broadcast','continuarPartida')
        comenzar = True
    else:
        ##Esperamos que los jugadores se conecten
        print('[PARTIDA] ESPERANDO JUGADORES')
        conexion_player(AA_Engine)
        comenzar = generarPartida(AA_Weather)
    
    sleep(3)
    if comenzar:
    ##Creamos la partida y empezamos a jugar
        comenzarPartida()
    else:
        print(ERR_MATCH)
        Broker = Modulo('Broker')
        Broker.setIPfromJson('Broker')    
        enviarMensaje(Broker,'broadcast', 'finTiempo')
if __name__ == "__main__":
    main()

    