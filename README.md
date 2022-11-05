
# Mapa

El mapa consiste en un tablero de 20x20, formado por cuatro cuadrantes de 10x10. Cada cuadrante corresponde a una ciudad distinta.
Cada vez que un jugador cambia de ciudad, se le cambia el cuadrante en el que está posicionado
</br></br>

<img src=documentacion/mapa.jpg width=400px height=400px>

Al crear una instancia de la clase mapa, se iniciará una matriz N x N, donde N es el número de ciudades.

```python
class Mapa:

    def __init__(self):
        self.ciudades = [ [ 0 for i in range(NUM_CITIES//2) ] for j in range(NUM_CITIES//2) ]
```

Cuando añadimos una ciudad, se le debe pasar las posiciones del cuadrante donde va a posicionarse.
```python
    def addCiudad(self,i,j,ciudad):
        self.ciudades[i][j] = ciudad
```

Para imprimir el mapa, primero recorremos la primera fila de ciudades ( [0][i] donde i varía entre 0 y 1 ) y luego la segunda fila de </br> ciudades 
( [1][i] donde i varía entre 0 y 1 )
```python
    def __str__(self):
        ...

        for fil in range(TAM_CIUDAD):
            ...

            for i in (0,1):
                c+= self.ciudades[0][i].str(fil)
                ...

        for fil in range(TAM_CIUDAD):
            ...

            for i in (0,1):
                c+= self.ciudades[1][i].str(fil)
                ...
        ...
```

# Ciudad

Cada ciudad estrá formada por un tablero de 10x10 en las que se almacena:
- Nombre
- Temperatura
- Posiciones Minas
- Posiciones Alimentos
- Posiciones Jugadores
- Posiciones NPC's
</br>

<img src=documentacion/ciudades.jpg width=500px height=500px>

La clase ciudad está creada de tal manera que se crea una matriz de 10x10, donde en cada casilla se posicionará una entidad u otra. Se generarán los parámetros de número de minas y número de alimentos aleatoriamente.
```python
MIN_ALIMENTOS = 15; MAX_ALIMENTOS = 25
MAX_MINAS = 25; MIN_MINAS = 15
NUM_CITIES = 4; TAM_CIUDAD = 10


class Ciudad:
    def __init__(self,nombre,temperatura,tam):
        self.casillas = [ [ 0 for i in range(TAM_CIUDAD) ] for j in range(TAM_CIUDAD) ]
        self.nombre = nombre
        self.temperatura = temperatura
        self.alimentos = random.randint(MIN_ALIMENTOS,MAX_ALIMENTOS)
        self.minas = random.randint(MIN_MINAS,MAX_MINAS)
        self.tam = tam
```

En el método empleado para imprimir una ciudad, se le pasa como parámetro la fila seleccionada y se le devolverá la fila completa de las entidades que se almacenan en cada casilla.

```python

    def str(self, i):

        ...

        for j in range(TAM_CIUDAD):
            c+=str(self.casillas[i][j])
            ...

        return c
```

`TODO: implementar y documentar el método setCasillas`

# Jugador

La clase jugador representa a los jugadores que intervienen en la partida. Se compone de:

- Alias: Identificador del jugador. Se utiliza en el login, y para identificar el receptor de los mensajes enviados a todos los jugadores
- AliasCorto: Es la primera letra del identificador del jugador, y sirve para ubicar al jugador en el mapa.
- CiudadX, CiudadY: Coordenadas de la ciudad en la que está el jugador
- PosX, PosY: Coordenadas de la posición que ocupa el jugador en una determinada ciudad.
- EF, EC: Modificadores de frío y calor, que se aplican según sea la temperatura de la ciudad en la que está el jugador.
- Nivel: Nivel de combate del jugador. Sirve para decidir si el jugador gana o pierde, cuando se choca con otro jugador o NPC. Se incrementa cuando el jugador come un alimento, y se pone a -99 cuando el jugador muere, bien a manos de otro jugador, o bien porque ha pisado una mina.
- NivelReal. Nivel efectivo del jugador, que resulta de aplicar el modificador de frío o calor al nivel del jugador.


# Módulos

Cada módulo representan los servidores o clientes de la partida.

Se han definido distintos módulos dentro de un fichero JSON:
```json
{
    "direcciones": [
        {
            "Id": "AA_Engine",
            "IP": "x.x.x.x",
            "port": "x"
        },
        {
            "Id": "Broker", 
            "IP": "x.x.x.x",
            "port": "x"
        },
        {
            "Id": "AA_Registry",
            "IP": "x.x.x.x",
            "port": "x"
        },
        {
            "Id" : "AA_Weather",
            "IP" : "x.x.x.x",
            "port": "x"
        }
    ]
}
```

Para representarlos y crear instancias con la clase **Modulo**:
```python
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

```

De esta manera, serán mucho más fácil instanciar y conseguir las direcciones a las que conectarse. Por ejemplo para crear una conexión con el módulo AA_Engine, tan sólo tendriamos que indicar su id y ya podríamos conseguir sus direcciones:

```python
AA_Engine = Modulo('AA_Engine')

ip = AA_Engine.getIp()
port = AA_Engine.getPort()

```

## Jugador

El jugador (*AA_Player*) será el que podrá registrarse en la base de datos, actualizar sus datos o conectarse a una partida.

Al principio del programa, se le mostrará un menú con las distintas opciones

``` sh
Elige una opción:
1. Crear perfil
2. Editar perfil
3. Unirse a partida
4 Salir

> Tu opción: 
```

### Crear perfil

La opción *Crear perfil* llamará a la función `insertRegistry(AA_Registry)`, que leerá el alias y contraseña introducidos por el usuario convirtiéndolo en *string*, con formato *JSON*. Se enviará un mensaje al servidor con la confirmación de que va a insertar y envia vía socket los datos.

```python
datos = {   "alias":     input('alias: '), 
            "password": input('password: '),
            "nivel":    '1',
            "ef":       '0',
            "ec":       '0'
         }
datos = json.dumps(datos)
    
conn.connect((AA_Registry.getIp(), AA_Registry.getPort()))
    
conn.send('insert'.encode())
msg = conn.recv(1024).decode()
                
conn.send(datos.encode())
msg = conn.recv(1024).decode()
```

### Editar perfil

A la hora de editar el perfil, se cambiará la contraseña del jugador, indicando su alias y contraseña.

```python
data = {    "alias": input('old alias: '),
             "password": input('password: ')
        }
oldData = json.dumps(data)

data = {    "password": input('new password: ') }
newData = json.dumps(data)

conn.send('update'.encode())
msg = conn.recv(1024).decode()

conn.send(oldData.encode())
msg = conn.recv(1024).decode() 

conn.send(newData.encode())
msg = conn.recv(1024).decode()

```

### Unirse a partida

Cuando un jugador intenta conectarse a una partida, primero deberá pasar por un estado de verificación, donde el jugador registrado introducirá su alias y contraseña para enviarlos mediante una conexión por sockets al servidor AA_Engine.

```python
import socket

def conectarPartida(Broker, AA_Engine):

    engine_socket = socket.socket()
    engine_socket.connect((AA_Engine.getIp(),AA_Engine.getPort()))

    msg = engine_socket.recv(1024).decode() 

    login = {   'alias' : input('Alias: '),
                'password' : input('Password: ')
            }

    login = json.dumps(login)

    engine_socket.send(login.encode())

    data = engine_socket.recv(1024).decode()
    data = json.loads(data)

    if data['verified']:
        jugarPartida(Broker)

    engine_socket.close()

    return

```

Si el jugador se ha logueado sin problemas, podrá empezar con la partida enviando produciendo unos movimientos, que serán W (west) , S (south), E (east), N (north). El envío se realizará mediante el servicio **Kafka** y habrá un tiempo de espera hasta introducir el siguiente movimiento.

```python
from kafka import KafkaProducer
from time import sleep

def jugarPartida(Broker):

    producer = KafkaProducer(bootstrap_servers=[f'{Broker.getIp()}:{Broker.getPort()}'],
                         value_serializer=lambda x: 
                         json.dumps(x).encode('utf-8'))

    while True:
        data = {'move' : input('Choose your direction (E,W,S,N): ')}
        producer.send('player_move', value=data)
        sleep(5)
```



`TODO: completar código y descripción con implementación final`


## Registro

El registro (*AA_Registry.py*) se encarga de almacenar los datos de un jugador.

Estará indefinidamente escuchando conexiones entrantes del módulo *AA_Player* y dependiendo de la petición recibida, procederá realizar una acción u otra
````python
while(True):

    # conectamos con el cliente
    c, address = register_socket.accept()  
    print("Connection from: " + str(address))

    # decodifica los datos enviados para que se puedan leer y procesar
    option = c.recv(1024).decode()
    if option == 'insert':
        inserting(c)
    
    elif option == 'update':
        updating(c)

    c.close()
````
Las opciones que tendrá un jugador serán de insertar un registro en la base de datos o actualizarlo. Los datos recibidos serán del tipo string, que convertiremos al formato **JSON**. Se enviará un mensaje acerca del estado final de la consulta:

````python
    dataReceived = c.recv(1024).decode()
    
    dataJson = json.loads(dataReceived)
````

````python
    if mongoInsert(dataJson):
        c.send('Inserted succesfully !'.encode())
    else:
        c.send('Error while inserting !'.encode())
````

````python
    if mongoUpdate(dataJson):
        c.send('Updated succesfully !'.encode())
    else:
        c.send('Error while inserting !'.encode())
````

La base de datos usada es MongoDB (nombrada gameBD) conectándose de la siguiente manera a la BD:
````python
try:
    conn = MongoClient()
    print("Connected to MongoDB successfully!!!")
except:  
    print("Could not connect to MongoDB")
    return False

db = conn.gameDB
collection = db.players
````

- Insertar/Registrar usuario. Siempre que **no exista** un usuario con el **mismo nombre**, se podrá registrar un jugador.
    ````python
    # Si no ha encontrado a nadie con el mismo alias, inserta
    if findPlayer(collection,{'alias' : data['alias']}):
       return False

    try:
       collection.insert_one(data)
    
    except pymongo.errors.PyMongoError as e:
       print(e)
       return False
    
    print('Inserted!')
    return True
    ````
- Actualizar. Se podrá actualizar un usuario **si y sólo si existe** en la base de datos
    ````python
    try:
        # buscamos al jugador con el mismo alias y password, y actualizamos el password
        result = collection.find_one_and_update(
            {
                'alias': oldData['alias'],
                'password': oldData['password']
            },
            {'$set': { 
                'password':newData['password']
                }
            }
        ) 
        # si no se ha actualizado ningún registro, devuelve error
        if result == None or not result.matched_count > 0:
            return False

    except pymongo.errors.PyMongoError as e:
        print(e)
        return False

    print('Updated!')
    return True
    ````


## Clima

El clima (*AA_Weather.py*) se encarga de estar a la espera de peticiones del engine (*AA_Engine.py*) para enviar una ciudad aleatoria de su base de datos.

Para la base de datos, se ha usado esta vez un archivo de JSON:
````json
{
    "ciudades": [
        {
            "nombre": "Londres",
            "temperatura": "5"
        },
        {
            "nombre": "Alicante",
            "temperatura": "26"
        },
        
        .
        .
        .
        
    ]
}
````
 
Se va a realizar una conexión por medio de sockets al engine (*AA_Engine.py*):
````python
import socket

AA_Engine =  Modulo('AA_Engine')

conn = socket.socket() 
conn.bind((AA_Engine.getIp(), AA_Engine.getPort())) 

conn.listen(2)
````

Aceptará conexiones indefinidamente y cada vez que se conecte, se realizará el envío y recibos de mensajes. En caso de que el mensaje sea *ok*, se dejarán de enviar las peticiones de ciudades. Las ciudades se enviarán en formato string, convertido por ``json.dumps()``, para facilitar la recepción de mensajes.
````python
import json

while True:
    engine, address = conn.accept()  
    while peticion != 'ok':
        peticion = engine.recv(1024).decode()
        city = json.dumps(chooseCity())
        engine.send(city.encode())
````

El mecanismo para elegir las ciudades aleatoriamente, será con el uso del módulo de python **random**

````python
import random

def chooseCity():
    file = open('src/json_files/data.json')
    data = json.load(file)
    file.close()

    indx = random.randrange(0,MAX_CITIES) 

    return data['ciudades'][indx]
````

## Motor

El motor del juego (*AA_Engine*) se basa en implementar la lógica del juego y el servidor central de la comunicación entre procesos.

En primer lugar, el servidor estará escuchando en un puerto para que los jugadores puedan conectarse. Una vez aceptadas las peticiones, se crearán varios hilos por cada conexión.

```python
conn, addr = engine_socket.accept()  

thread = threading.Thread(target=handle_player, args = (conn,addr,Broker))
thread.start()
```
La función que se encargará de manejar dichos hilos, será `handle_player`, en donde se verificará la existencia del jugador en la base de datos. En caso de existir, se registrará al jugador en la partida, incrementando el número de jugadores conectados.

```python
def handle_player(conn,addr,AA_Broker):

    jugador = autentificarJugador(conn)

    if jugador != False:
        objetoJugador = Player(jugador['alias'], jugador['nivel'])
        arrayJugadores.append(objetoJugador)
        data = {    'msg' : 'Conectando a partida...',
                    'verified' : True
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

```



Cuando se ha alcanzado el límite de jugadores, la partida debe arrancar. Para ello, hay que generar el mapa de juego, que consiste en los siguientes pasos:
- Generación de ciudades: Es un proceso en el que se realizan varias peticiones de información al servidor de clima. Este nos devuelve una ciudad y su temperatura asociada. Como tenemos que tener cuatro ciudades distintas, realizamos todas las peticiones que sean necesarias a este servidor, hasta tener esas ciudades no repetidas.
- Colocación de jugadores: Colocamos a cada uno de los jugadores en una casilla aleatoria, de cualquier ciudad disponible.
- Rellenado del mapa de ciudades: Para cada una de las ciudades, se genera un número aleatorio de alimentos y minas, y se colocan en el mapa, cuidando de no colocar ningún elemento en una casilla que ya esté ocupada.

Con el mapa relleno, ya puede comenzar la partida. Mediante la tecnología de **kafka**, se depositan en las respectivas colas los mensajes con el mapa, y el inicio de la partida. A partir de aquí, la aplicación ejecutará indefinidamente el método  `escucharMovimientos()`. 

Cuando un jugador se conecte a una partida, se hará uso de la tecnología de **kafka** para escuchar los movimientos recibidos del productor ( *AA_Player* ). El método `escucharMovimientos()` , estará consumiendo dichos movimientos.

```python
from kafka import KafkaConsumer


def escucharMovimientos(Broker):
    consumer = KafkaConsumer(
    'player_move',
     bootstrap_servers=[f'{Broker.getIp()}:{Broker.getPort()}'],
     auto_offset_reset='earliest',
     enable_auto_commit=True,
     group_id='my-group',
     value_deserializer=lambda x: json.loads(x.decode('utf-8')))

    for message in consumer:
        message = message.value
        print('{} move registered '.format(message))
```

`TODO: completar código y descripción con implementación final`

# Steps:

1.  Install [docker](https://www.docker.com/products/docker-desktop/)
2.  Install [offset explorer 2](https://www.kafkatool.com/download.html)
3.  Install [mongoDB compass](https://www.mongodb.com/try/download/compass), [mongosh](https://www.mongodb.com/docs/mongodb-shell/install/) 
    and [mongodb-community](https://www.mongodb.com/docs/manual/administration/install-community/)
4.  Run docker-compose up -d
5.  Test


## Test Kafka

1.  Run docker-compose up -d
2.  Open Offset Explorer
3.  Run kafka_producer.py
4.  Run kafka_consumer.py


## Test AA_Registry-AA_Player

1. Open MongoDB Compass 
2. Start mongodb service (if neccesary):
    - MACOS: brew services start mongodb-community
    - Linux: sudo service mongodb start
4. Run AA_Registry.py
5. Run AA_Player.py

## Consideraciones cuando un jugador entra en una partida

- Los factores de clima frío y calor se deben generar aleatoriamente cuando un jugador entra en la partida. Los valores son entre -10 y +10
- Cuando un jugador cambia de cuadrante, se debe aplicar el factor de frío o calor, según sea la temperatura de la ciudad donde entra
- Los factores de clima permanecen constantes durante toda la partida
- Los factores de clima se deben almacenar en base de datos, junto con el nivel y posición del jugador, por si el AA_Engine cae, y tiene que recuperar la partida
