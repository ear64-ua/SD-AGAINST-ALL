
# Mapa

El mapa consiste en un tablero de 20x20 que va a estar fornada por cuatro cuadrantes en las que cada una de ellas estará representando una ciudad.
Cada vez que un jugador cambia de ciudad, se le cambia el cuadrante en el que está posicionado
</br></br>

<img src=documentacion/mapa.jpg width=400px height=400px>

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
msg = conn.recv(1024).decode() # confirmación de datos antiguos

conn.send(newData.encode())
msg = conn.recv(1024).decode() # confirmación de insert

```

### Unirse a partida

...


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
