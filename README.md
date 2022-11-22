# Clases

## Mapa

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

## Ciudad

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


## Jugador

La clase jugador representa a los jugadores que intervienen en la partida. Se compone de:

- Alias: Identificador del jugador. Se utiliza en el login, y para identificar el receptor de los mensajes enviados a todos los jugadores
- AliasCorto: Es la primera letra del identificador del jugador, y sirve para ubicar al jugador en el mapa.
- CiudadX, CiudadY: Coordenadas de la ciudad en la que está el jugador
- PosX, PosY: Coordenadas de la posición que ocupa el jugador en una determinada ciudad.
- EF, EC: Modificadores de frío y calor, que se aplican según sea la temperatura de la ciudad en la que está el jugador.
- Nivel: Nivel de combate del jugador. Sirve para decidir si el jugador gana o pierde, cuando se choca con otro jugador o NPC. Se incrementa cuando el jugador come un alimento, y se pone a -99 cuando el jugador muere, bien a manos de otro jugador, o bien porque ha pisado una mina.
- NivelReal. Nivel efectivo del jugador, que resulta de aplicar el modificador de frío o calor al nivel del jugador.
- Tipo. clase de jugador, que puede 'PC' (jugador humano) o 'NPC' (jugador artificial)


## Módulos

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

Para representarlos y crear instancias con la clase **Modulo**, siendo posible generar el puerto del fichero JSON o del argumento del programa. De esta manera, serán mucho más fácil instanciar y conseguir las direcciones a las que conectarse. Por ejemplo para crear una conexión con el módulo AA_Engine, tan sólo tendriamos que indicar su id y ya podríamos conseguir sus direcciones:

```python
AA_Engine = Modulo('AA_Engine')
AA_Engine.setIp(args[0])

Broker = Modulo('Broker')
Broker.setIPfromJson('Broker')

```


# Kafka

## Estructura y mensajes

Para articular la comunicación de la práctica, definimos una partición con tres topics. Los topics son:

1. player_move
2. mapa
3. estadoJugador

Definimos la funcionalidad de los topics, así como la estructura de mensajes que contienen. **IMPORTANTE**. Todos los mensajes incluyen un identificador de partida. Este mensaje sirve para poder ejecutar varias partidas de forma simultánea, y que cada parte del sistema lea solamente los mensajes que corresponden a su partida. Hecha esta aclaración, pasamos a los topics:

1. player_move: Este topic sirve para que las aplicaciones de jugador escriban el movimiento que desean hacer sobre el tablero. Las aplicaciones que pueden escribir en este topic son AA_Player y AA_NPC, y los mensajes son consumidos por AA_Engine. Sólo hay un tipo de mensaje válido, con la siguiente estructura:

```
    data = {'alias': alias del jugador que realiza el movimiento,
            'codigoPartida': identificador de la partida en curso,
            'numMovimiento': código del movimiento efectuado (funcionalidad de resiliencia)
            'move' : dirección hacia la que se mueve el jugador (N, S, E, W, NE, NW, SN, SW )
            }
```
Hay un mensaje especial de control de final de partida por tiempo, en el que el propio AA_Engine escribe en el topic, y consume su propio mensaje. Este mensaje tiene la siguiente estructura:
```
        data = {'finTiempo' : True,
                'codigoPartida' : codigoPartida}
```

2. mapa: Este topic sirve para que los jugadores puedan mostrar por pantalla el mapa de juego. Sólo escribe en él la aplicación AA_Engine, y los mensajes son consumidos por las distintas aplicaciones AA_Player que haya arrancadas. En el topic puede haber dos tipos de mensajes:

        data = {'mapa': mapa,
                'codigoPartida' : codigoPartida}

        data = {'finPartida': True,
                'codigoPartida' : codigoPartida}

 El primer mensaje contiene un string con el mapa del mundo, y se utiliza para que los jugadores puedan imprimir el mapa del mundo.  
 El segundo mensaje contiene un booleano que avisa de que la partida ha finalizado, y sirve para poder salir de los hilos y cerrar la aplicación AA_Player correctamente.

3. estadoJugador: Este topic sirve para varias cosas: comunicar la información de un jugador, coordinar el inicio y final de partida, reanudar una partida (resiliencia), y enviar ACKs de servidor online a los jugadores (resiliencia). Sólo escribe en él la aplicación AA_Engine, y los mensajes son consumidos por las distintas aplicaciones AA_Player y AA_NPC que haya arrancadas. En el topic puede haber tres tipos de mensajes:

        data = {'alias' : jugador.alias,
                'nivelReal' : jugador.nivelReal,
                'codigoPartida' : codigoPartida,
                'avatar' : jugador.avatar,
                'ciudad' : ciudad.nombre,
                'posX' : jugador.posX,
                'posY' : jugador.posY }

        data = {'broadcast': mensaje de broadcast,
                'codigoPartida' : codigoPartida}

        data = {'alias' : jugador.alias,
                'nivelReal' : jugador.nivelReal,
                'numMovimiento' : numMovimiento,
                'codigoPartida' : codigoPartida }

El primer mensaje representa la información de un jugador. Contiene el jugador al que va dirigido el mensaje, su nivel, su avatar, y la ubicación en el mapa. Toda esta información se utiliza en la interfaz de AA_Player, para dar información al usuario y que no vaya a ciegas por el mapa. Además, este mensaje también sirve para determinar la muerte de los jugadores. Cuando el nivel del jugador es -99, significa que ha muerto, así que debe salir del juego.  
El segundo mensaje es de broadcast, y va dirigido a todos los jugadores. El contenido del mensaje puede ser 'inicioPartida', 'reanudarPartida' o 'finPartida'. La primera opción indica a los jugadores que ya está todo preparado para iniciar la partida, y pueden empezar a leer mensajes de los dos topics. La segunda opción la veremos en el apartado de Resiliencia. La tercera opción indica que la partida ha terminado, y el único jugador que queda vivo mostrará un mensaje de victoria.  
El tercer mensaje es un ACK para que el jugador sepa que el servidor está funcionando. Lo veremos más detallado en la parte de resiliencia.

# Problemas encontrados y soluciones aplicadas

**Problema 1**: El primer problema que encontramos es que, cuando los jugadores tenían que leer los mensajes de los topics, cada mensaje era leído únicamente por uno de los jugadores. Al investigar el fallo, descubrimos que este fenómeno se producía porque todos los jugadores formaban parte del mismo grupo de lectura. Esto es un funcionamiento totalmente normal de kafka, pensado para facilitar la escalabilidad de las aplicaciones. El funcionamiento es que, cuando hay varias aplicaciones funcionando simultáneamente, por motivos de escalabilidad y tolerancia a fallos, solamente una de las aplicaciones del grupo leerá el mensaje. El resto no, para evitar que una misma tarea se repita varias veces. Así pues, para solucionar el problema, solamente tuvimos que __no definir el grupo__ al inicializar los diferentes objetos KafkaConsumer que hay en la práctica. De esta forma, la librería Kafka-python configura los objetos con un grupo distinto para cada uno.

**Problema 2**: Otro problema encontrado con Kafka en las primeras iteraciones de la práctica, correspondió a partidas que se juegan sucesivamente. El problema es que, precisamente por la configuración de grupos definida para solucionar el mensaje anterior, existe la posibilidad de que haya mensajes de partidas anteriores en el topic, que deban ser ignorados por los jugadores de una partida nueva. Existen varias formas de abordar la solución, y hemos tenido que implementar dos de ellas, porque en algunas situaciones había errores. La primera forma consiste en usar la función seek_to_end() de la librería de kafka-python, y definiendo el consumidor de la siguiente manera:

```python     
    assignments = []
    partitions = consumer.partitions_for_topic('mapa')
    for p in partitions:
        assignments.append(TopicPartition('mapa', p))    
    consumer.assign(assignments)
    consumer.seek_to_end()
```

Con este ajuste, leemos únicamente el último mensaje del topic 'mapa', ignorando todos los demás, que no tenemos que leer por ser mapas antiguos.

Esta solución no la pudimos emplear en el topic de estadoJugador, pues se comía el mensaje de broadcast de iniciar partida, así que hubo que definir algunas variables de control para ignorar todos los mensajes que no fueran el de 'broadcast' inicial.

Finalmente resultó que, al corregir el primer problema, el segundo desaparecía, por lo que no hay nada de esto en el código de la práctica. Pero hemos querido reseñarlo para ilustrar esta casuística que se puede producir en otras aplicaciones.

**Problema 3**: Un tercer problema encontrado fue que no éramos capaces de finalizar los programas al acabar las partidas, pues las distintas aplicaciones se quedaban activas indefinidamente, leyendo los topics de kafka. Resolvimos este problema mediante mensajes de coordinación (broadcast), que activan ciertas variables de control que se encargan de forzar el cierre del topic y finalizar el hilo de escucha. Especiamente complicado fue el cierre automático del hilo de captura de movimientos por parte del jugador humano. Barajamos el uso de algunas librerías de python, que implementan un input() con un timer, pero no nos gustaba el funcionamiento. Al final, la decisión tomada fue mostrar un mensaje de fin de partida por pantalla, e invitar al jugador a que pulse la tecla intro para salir.

**Problema 4**: Este problema está relacionado con los NPCs. Estos jugadores no humanos se identifican por una cadena con el formato n_NPC, siendo n el nivel del NPC generado. El problema es que sólo podíamos tener un NPC de cada nivel en el juego, y en cuanto se generasen 7-8 NPCs, coincidirían el nombre y se producirían colisiones en los movimientos. Solventamos este problema generando un número aleatorio entre 1 y mil millones, que se añade al final de la cadena, haciendo así que los NPCs sean únicos.

**Problema 5**: (Resiliencia). Este problema está relacionado con el código de partida que se genera al principio de cada ejecución. Al principio identificábamos la partida mediante un código aleatorio (como en los NPCs del problema 4), pero entonces nos dimos cuenta de que un servidor que se recuperaba tras una caída no iba a ser capaz de encontrar la partida que estaba ejecutando antes de la caída. La solución fue utilizar la IP del servidor como identificador de partida. Como al hacer el despliegue, se asignan IPs fijas, cada vez que un servidor se recupera, es capaz de mirar su IP y ver si hay alguna partida guardada en base de datos, y continuar con ella.

**Problema 6**: (Resiliencia). Este problema surge ante la imposibilidad de utilizar sockets entre la aplicación AA_Player y AA_Engine, salvo para la identificación inicial. Utilizando un socket, la detección de caída del servidor es inmediata, ya que no puede establecer la conexión. Al depender únicamente de Kafka, tuvimos que solucionar el problema mediante el sistema de ACKs descritos en la parte de resiliencia.

**Problema 7**: (Escalabilidad). Al toparnos con la escalabilidad de los servicios, nos dimos cuenta de que no podíamos asignar IP's estáticas o puertos a los contenedores si queríamos desplegar varios de ellos. Para ello hemos dejado que __docker__ sea el que nos asigne automáticamente las IP's de los servicios que sean desplegados. Estas direcciones asignadas serán recogidas por el script que hace correr el servicio que escojamos.

**Problema 8**: Existe un bug en los NPCs, no corregido, por el que cualquier NPC deja de moverse cuando muere en una partida. Este funcionamiento es correcto cuando solo hay una partida ejecutándose, pero es un fallo cuando hay varias partidas concurrentes. Debido a la complejidad artificialmente añadida en la práctica, de no poder registrar a un NPC en un servidor concreto, el bug queda sin corregir.

# Componentes software

## AA_Registry

Este módulo se encarga de almacenar los datos de un jugador en base de datos.

Estará indefinidamente escuchando conexiones entrantes del módulo *AA_Player* y dependiendo de la petición recibida, podrá insertar un nuevo jugador en base de datos, o editar uno existente

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
Los datos recibidos serán del tipo string, que convertiremos al formato **JSON**. Se enviará un mensaje acerca del estado final de la consulta:

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

## AA_Player

El módulo de jugador será el que podrá registrarse en la base de datos, actualizar sus datos o conectarse a una partida, para jugar.

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

### Jugar partida

Si el jugador se ha identificado correctamente, puede empezar la partida. Para ello, la aplicación utiliza tres hilos. Uno de estos hilos solicita al usuario el movimiento que desea realizar, y lo envía al servidor. Los otros dos hilos leen datos enviados por el servidor, y la aplicación procesa la información.

```python
    t1 = threading.Thread(target=insertarMovimiento, args = [Broker])
    t2 = threading.Thread(target=leerMapa, args = [Broker])
    t3 = threading.Thread(target=leerEstado, args = [Broker])
```

Describimos cada uno de los hilos:

- El hilo 'leerEstado' es el encargado de toda la lógica interna del programa. Para ello, lee los mensajes depositados por el servidor en el topic 'estadoJugador' de **Kafka**. Estos mensajes sirven para activar o desactivar las variables de control 'jugadorVivo', 'ackRecibido' y 'partidaIniciada', que se utilizan para arrancar y parar la aplicación, determinar si el servidor está funcionando, y decidir qué mensajes se muestran por pantalla al usuario. 

- El hilo 'insertarMovimiento' es un bucle que lee de consola el movimiento que desea realizar el usuario. Las direcciones podrán ser N (arriba), S (abajo), E (derecha), W (izquierda), NE (arriba-derecha), NW (arriba-izquierda), SE (abajo-derecha), SW (abajo-izquierda). El envío se realizará mediante el topic 'player_move' de **Kafka** y habrá un tiempo de espera de un segundo hasta que se pueda introducir el siguiente movimiento.

```python
        data = {'alias': alias,
                'codigoPartida' : codigoPartida,
                'numMovimiento' : numMovimientos,
                'move' : input()}       
        if(jugadorVivo and partidaIniciada):        
            producer.send('player_move', value=data)
```

Adicionalmente, el hilo es capaz de verificar si el servidor está funcionando o no. Si el servidor no está activo, muestra un mensaje informativo por pantalla y no envía ningún movimiento al servidor. Detallamos este funcionamiento en profundidad, en el apartado de Resiliencia.

- El hilo 'leerMapa' se encarga de leer el mapa y mostrarlo por pantalla. La lectura se realiza en el topic 'mapa' de **Kafka**. Como detalle importante, es en este hilo donde se muestra al mensaje de "Elige tu movimiento". Está puesto aquí por motivos de claridad en la interfaz, ya que, si se ponía en el hilo 'insertarMovimiento', se mostraba primero el mensaje y luego el mapa, y el jugador podría no saber qué hacer a continuación. 

```python
    for message in consumer:
            if(jugadorVivo):
                message = message.value
                if(message['codigoPartida']) == codigoPartida:
                    if('mapa' in message):
                        mapa = message['mapa']
                        print(mapa)
                        print('Elige tu movimiento (N, S, E, W, NE, NW, SE, SW): ')
```

## AA_Weather

El servidor de clima se encarga de estar a la espera de peticiones del engine (*AA_Engine.py*) para enviar una ciudad aleatoria de su base de datos.

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

## AA_Engine

El motor del juego se basa en implementar la lógica del juego y el servidor central de la comunicación entre procesos.

Al arrancar el servidor, se realiza la carga de los parámetros de configuración desde un fichero externo, y se determina la IP del Engine, que servirá como código identificador de partida.  
A continuación, el motor queda a la espera de la conexión de los jugadores. Esto se hace mediante un hilo, para poder aceptar varios jugadores de forma concurrente. La tecnología utilizada es sockets, y se ha implementando una lógica de control para impedir que se puedan conectar a la partida más jugadores que el máximo establecido:

```python
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

Con el mapa relleno, se genera un mensaje de broadcast de inicio de partida, se envía el mapa inicial a los jugadores, y se lanzan dos hilos en paralelo.

    enviarMensaje(Broker,'broadcast', 'inicioPartida')
    enviarMensaje(Broker, 'mapa', None)
    t1 = threading.Thread(target=escucharMovimientos, args = [Broker])
    t2 = threading.Thread(target=finalizarPartidaPorTiempo, args = [Broker])

 El primer hilo lleva la cuenta del tiempo transcurrido, y cuando se alcanza el tiempo límite, envía a todos los jugadores (y a sí mismo) una serie de mensajes que desencadenan el final de la partida

```python
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
```
El segundo hilo está indefinidamente leyendo el topic de **kafka** que contiene los movimientos de los jugadores. Tiene como condición de salida la recepción del evento de límite de tiempo, o que sólo quede un jugador vivo. Mientras no se cumpla alguna de estas dos condiciones, el hilo realiza una serie de tareas, que detallamos a nivel pseudocódigo:

```
 def escucharMovimientos(Broker):
    consumer = KafkaConsumer(...)
    for message in consumer:
        - comprueba que el mensaje contiene el código de partida correcto
        - analiza el mensaje para saber si es de movimiento o de final de partida. Si es final de partida, sale del bucle. Si es de movimiento:
            - determina si el movimiento proviene de un jugador o un NPC, y si está vivo. En caso de no estar vivo, el movimiento no se analiza
                - Si es NPC: 
                    - lo añade a una lista de NPCs si no existe ya en la partida.
                    - mueve al jugador. 
                    - determina si ha matado a un jugador u otro NPC.
                    - actualiza el mapa.
                - Si es jugador: 
                    - envía un ACK de recepción de mensaje
                    - mueve al jugador al destino
                    - actualiza el nivel del jugador con el bonus de frío o calor correspondiente a la ciudad en la que está
                    - comprueba la casilla destino:
                        - Alimento: incrementa el nivel
                        - Mina: el jugador muere y se activa la lógica de final de partida, si sólo queda otro jugador vivo
                        - Jugador o NPC: Mata a otro jugador si su nivel es mayor, o muere si su nivel es menor. Empatan si tienen el mismo nivel. Se activa la lógica de final de partida, si sólo queda otro jugador vivo
                    - actualiza el mapa
            - Envía mensajes a la cola correspondiente, con el mapa y la muerte de un jugador (si procede)
            - borra la partida grabada anterior (Resiliencia)
            - graba la nueva partida (Resiliencia)   
```

## AA_NPC

El módulo de jugadores no humanos es similar en su concepción al de los jugadores humanos, pero con un par de cambios. En este módulo, los NPCs vuelcan directamente su movimiento en la cola de mensajes, sin tener que pasar por un proceso de registro. 
Al igual que el AA_Player, la aplicación utiliza tres hilos. Uno de estos hilos genera el movimiento aleatoriamente, y lo envía al servidor. Los otros dos hilos leen datos enviados por el servidor, y la aplicación procesa la información.

```python
    t1 = threading.Thread(target=insertarMovimiento, args = [Broker])
    t2 = threading.Thread(target=leerMapa, args = [Broker])
    t3 = threading.Thread(target=leerEstado, args = [Broker])
```

Describimos cada uno de los hilos:

- El hilo 'leerEstado' es el encargado de toda la lógica interna del programa. Para ello, lee los mensajes depositados por el servidor en el topic 'estadoJugador' de **Kafka**. Estos mensajes sirven para activar o desactivar las variables de control 'jugadorVivo' y 'partidaIniciada', que se utilizan para arrancar y parar la aplicación, y decidir qué mensajes se muestran por pantalla al usuario. 

- El hilo 'insertarMovimiento' es un bucle que calcula de forma automática el movimiento que desea enviar al servidor, eligiendo al azar una de las ocho direcciones disponibles. El envío se realizará mediante el topic 'player_move' de **Kafka**. Además, para no saturar la cola de movimientos, hemos tomado la decisión de que los NPCs se muevan una vez cada cinco segundos.

```python
    indice = random.randint(0,len(arrayMovimientos)-1)
    data = {'alias':            alias,
            'codigoPartida':    'NPC',
            'move' :            arrayMovimientos[indice],
            'nivel':            nivel
            }
    print(data)               
    if(jugadorVivo):        
        producer.send('player_move', value=data)
    sleep(5)
```

- El hilo 'leerMapa' se encarga de leer el mapa y mostrarlo por pantalla. La lectura se realiza en el topic 'mapa' de **Kafka**. 

```python
    for message in consumer:
            if(jugadorVivo):
                message = message.value
                if(message['codigoPartida']) == codigoPartida:
                    if('mapa' in message):
                        mapa = message['mapa']
                        print(mapa)
                        print('Elige tu movimiento (N, S, E, W, NE, NW, SE, SW): ')
``` 

# Resiliencia

Detallamos a continuación los efectos de la caída de cada módulo, y qué ocurre cuando vuelve a funcionar.

## AA_Registry

El módulo de registro sólo es necesario cuando un jugador se intenta dar de alta en el sistema. No afecta al desarrollo de las partidas.  
El efecto de la caída de este módulo es que se muestran mensajes de error en el módulo AA_Player, indicando que no se puede conectar al registro.  
Cuando el módulo se vuelve a arrancar, no se muestra ningún mensaje especial. Simplemente la funcionalidad de registro vuelve a funcionar.

## AA_Weather

El módulo de clima es necesario para la generación de nuevas partidas, y solamente en el momento de la creación de las mismas. Una vez se ha generado la partida, su caída es transparente para el resto de módulos.  
El efecto de la caída es que se muestra un mensaje de error en el servidor, se envía un mensaje broadcast de finTiempo a los módulos AA_Player, y se cierra la partida. Los jugadores reciben el mensaje broadcast, informa de que la partida no puede comenzar, y desconectan la aplicación.  
Cuando el módulo se vuelve a arrancar, no se desencadena ningún mensaje especial ni se hace ninguna acción específica.

## AA_NPC

El módulo de NPCs es un complemento a las partidas, y se puede caer en cualquier momento durante una partida. Cuando un NPC cae, no afecta en nada al resto de componentes de la partida.  
El efecto de la caída es que la aplicación deja de enviar mensajes a la cola de movimientos. El servidor no es capaz de saber que este módulo ha caído, por lo que simplemente mantiene al jugador NPC en el mapa, sin moverse, hasta que otro NPC o un jugador lo mate.  
Cuando el módulo se vuelve a arrancar, se genera un nuevo NPC, que se mueve de forma independiente al NPC anterior que cayó.

## AA_Player

El módulo de jugadores es una parte importante de la partida. Funciona de manera similar a los NPCs. Esto es, cuando un jugador cae, se considera que ya no puede volver a entrar en la partida. No hemos diseñado un mecanismo de reconexión a la partida, aunque dicha partida siga en marcha.  
El efecto de la caída es que la aplicación deja de enviar mensajes a la cola de movimientos. El servidor no es capaz de saber que este módulo ha caído, por lo que simplemente mantiene al jugador en el mapa, sin moverse, hasta que otro jugador o un NPC lo mate.  
Cuando el módulo se vuelve a arrancar, se genera un nuevo jugador, que funciona de forma totalmente independiente al jugador anterior que cayó. Tendrá que conectarse a una nueva partida, etc.

## AA_Engine

El módulo del motor del juego es crucial en la partida, y es donde hemos dedicado más esfuerzo en su recuperación. Este módulo es la base de todo el juego, y si cae, los jugadores dejan de poder jugar.  
El efecto de la caída es que la aplicación deja de leer las colas de movimiento, y de escribir mensajes. Al no leer colas, es posible que los jugadores metan muchos datos, que al final no van a ninguna parte. Por ello, hemos creado un sistema de ping y ACK utilizando Kafka, ya que no está permitido utilizar sockets, que es la forma más sencilla que hay de implementar este ping-pong.   
El mecanismo de ping-pong es el siguiente: Cuando un jugador inserta un movimiento, envía al Engine, mediante la cola de movimientos, un código numérico. Este código debe ser devuelto mediante la cola de control al jugador. Si el mensaje le llega en el siguiente segundo, el jugador sigue funcionando con normalidad. Si no llega el mensaje, el jugador detiene el envío de movimientos, y queda a la espera de recibir un mensaje de que el servidor se ha recuperado.  
Cuando el módulo se vuelve a arrancar, este comprueba si hay una partida guardada que pertenezca al servidor. De ser así, se procede a recargar todos los datos importantes de la partida (mapa, ciudades, lista de jugadores que pertenecían a la partida), y se envía un mensaje de broadcast de reconexión. Gracias a este mensaje, en cada módulo de jugador que esté activo se muestra un mensaje de recuperación, y los jugadores recuperan la funcionalidad, volviendo a funcionar el módulo de jugador con normalidad. 

## Consideraciones cuando un jugador entra en una partida

- Los factores de clima frío y calor se deben generar aleatoriamente cuando un jugador entra en la partida. Los valores son entre -10 y +10
- Cuando un jugador cambia de cuadrante, se debe aplicar el factor de frío o calor, según sea la temperatura de la ciudad donde entra
- Los factores de clima permanecen constantes durante toda la partida
- Los factores de clima se deben almacenar en base de datos, junto con el nivel y posición del jugador, por si el AA_Engine cae, y tiene que recuperar la partida

# Requirements

Install [docker](https://www.docker.com/products/docker-desktop/)

# Despliegue

En el despliegue se ha hecho uso de los contenedores de Docker. Nos hemos encotrado con problemas al asignar IP's estáticas , ya que al estar definidas en ``docker-compose.yml`` , si un servicio se quiere escalar, no sería posible ya que estaría ocupando la misma dirección IP. Para solucionar esto, dejamos que Docker sea el que nos proporcione las direcciones, ya que al permitirnos crear una red interna, sus componentes se conectan al adaptador ``Docker 0`` , que actúa como un switch, y sería la puerta por defecto de nuestra red. Al no conocer las IP's que nos van a proporcionar a nuestros servicios, tenemos el problema de que no sabemos dónde conectarnos de un módulo cliente a un módulo servidor. Para ello, se ha hecho uso de scripts, que nos filtrarán las direcciones de cada contenedor desplegado. Tras usar ``docker compose up -d --scale aa_player=x`` , no nos tendríamos que preocupar de que un mismo servicio se tenga que conectar con una IP ya usada. El parámetro ``--scale`` nos permite escalar el número de instancias de un determinado servicio.
El despliegue quedaría de la siguiente manera:


<img src=documentacion/docker.jpg width=400px height=400px>


Y lo desplegaríamos ejecutando en ``/src`` lo siguiente:
`./run.sh`

## Correr servicios

#### AA_Engine
``./run_engine``

#### AA_Weather
``./run_weather``

#### AA_Registry
``./run_registry``

#### AA_Player
``./run_player``

#### AA_NPC
``./run_npc``

## Parar servicios

``./stop.sh``

## Eliminar servicios

``./clean.sh``






