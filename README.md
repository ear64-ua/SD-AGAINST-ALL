

# Problemas encontrados y soluciones aplicadas

**Problema 1**: 

**Problema 2**: 

**Problema 3**: 

**Problema 4**: 

**Problema 5**: 

**Problema 6**: 

**Problema 7**: Al utilizar la auditoría de eventos mediante la librería estándar, nos encontramos con que el servidor Flask también depositaba sus mensajes en el fichero de log, y esto es algo que no queríamos. Para solucionarlo, hemos optado por desactivar los mensajes de Flask, mediante la instrucción ``logging.getLogger('werkzeug').disabled = True``

**Problema 8**: Al añadir SSL a la API Rest, nos hemos encontrado con una serie de mensajes de error, derivados de que los certificados son autofirmados, en vez de ser generados por una entidad certificadora reconocida. Para evitar estos mensajes, ya que no vamos a tener los certificados correctos, hemos optado por desactivar la validación de los certificados, mediante un parámetro añadido a las instrucciones de request: ``requests.post(api_request, verify=False)``

## Generación de certificados

El mecanismo de autenticación, sockets seguros y codificación de datos en Kafka requiere una serie de certificados para cada uno de los servidores implicados en el proceso. Para generar los certificados, hemos utilizado la herramienta de openssl incluida en Ubuntu. Los hemos generado mediante el comando ``openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes``, que solicita además un montón de datos sobre la persona/entidad que va a utilizar el certificado. Este comando lo hemos utilizado dos veces, uno para los certificados de AA_Registry, y otro para los certificados de AA_Engine. Una vez estaban generados los certificados, los hemos movido a las respectivas carpetas 'secrets' de cada módulo.

## Auditoría de eventos en Registry

Para realizar la auditoría de eventos en Registry, hemos utilizado la librería estandar de log de python. Los eventos que registramos son ocho: creación y actualización de un jugador mediante API rest, y creación y actualización de un jugador mediante sockets. Los otros cuatro eventos corresponden a los posibles errores que se produzcan al realizar esas operaciones. Los eventos informativos se registran mediante la etiqueta 'info', y los eventos de error quedan registrados con la etiqueta 'error'. Cada uno de estos mensajes tienen además, la fecha y hora cuando se produjeron, y la IP del módulo que generó el mensaje. Por último, los mensajes los escribimos en un fichero de log, con el formato ``registryYYYYmmdd.log``. 

## Cifrado de los datos entre Engine y Players

Para securizar el socket de ingresar en una partida nos hemos decantado por la codificación asimétrica. Es un método igual de seguro que la simétrica, y muy fácil de implementar. El funcionamiento de los sockets seguros consiste en establecer una comunicación insegura al principio, para añadir después los certificados, y aunque los datos se pueden interceptar, estos van a ir codificados por los certificados.  
En la implementeción hemos tenido que cambiar algunas cosas en Engine y Player.
En Player, añadimos la capa segura a los sockets, mediante la instrucción de la librería SSL ``ssl_conn=ssl.wrap_socket(conn,ca_certs=engine_pem)``, donde registry_pem es la clave pública del Engine. Y el envío se datos se realiza a través de este socket seguro, dejando el inseguro simplemente para establecer la conexión.  
En Engine realizamos algo similar. El socket seguro se encapsula dentro del socket inseguro con la instrucción de la librería SSL ``ssl_socket=ssl.wrap_socket(c,server_side=True,certfile=engine_cert,keyfile=engine_key, ssl_version=ssl.PROTOCOL_TLSv1_2)``, donde se le indica que está en el lado del servidor, y las claves pública y privada de Engine, además del protocolo que se va a utilizar.

## Uso de API_Rest en AA_Registry

En esta sección, implementamos una API Rest en el módulo AA_Registry, para abrir el servicio de registro y modificación de datos. Al recopilar información sobre los distintos métodos de hacer la API, vimos que hay disponibles una gran cantidad de librerías y extensiones para Python. Al final, nos quedamos entre FastAPI y Flask, y elegimos esta última debido a que nos gustaba más la forma de recoger los parámetros introducidos por el cliente en la petición web, mejor estructurada que en FastAPI.  

El funcionamiento de Flask consiste en desplegar un servidor web, el cual va a recibir peticiones web. Con cada petición web, buscará si hay un método asociado a la petición, devolviendo la información necesaria al cliente que hizo la petición. Como en la práctica se pide que los Players deben poder conectarse mediante API y también mediante sockets, la forma más obvia de implementar ambos métodos fue mediante dos hilos. Uno de ellos arrancaría el servidor web, y el otro permanecería a la escucha de peticiones mediante sockets. 

El siguiente paso es añadir los dos métodos de api "registrar" y "actualizar". En ambos casos son de tipo "POST", ya que estamos introduciendo datos en el servidor. Ambos métodos hacen llamadas a métodos ya existentes en el código, que estaban siendo utilizados desde la práctica 1.

Finalmente, creamos y arrancamos el servidor web mediante ``app=Flask(__name__)`` y ``app.run(debug=False, port=8000, host="0.0.0.0")``

En el módulo AA_Player hemos introducido un par de cambios y añadidos. Lo primero ha sido añadir un menú inicial, en el cual se elige si la conexión con Registry es mediante API Rest o mediante sockets. El otro cambio ha sido la implementación de los métodos para consumir la API. El método Registrar contiene una url con los datos del nuevo usuario, de la forma ``api_request='http://'+ip+':8000'+'/registrar?data='+datos`` y posteriormente se ejecuta mediante la instrucción ``requests.post(api_request)``.   
El método Actualizar contiene una url con los datos de conexión, y los datos que se quieren actualizar, de la forma ``api_request='http://'+ ip+':8000'+'/actualizar?oldData='+oldData+'&newData='+newData``, y también se ejecuta mediante la instrucción ``requests.post(api_request)``.

## Mecanismos de seguridad entre Players y Registry

Para añadir seguridad al proceso de comunicación entre Players y Registry, hemos realizado tres añadidos. La contraseña del jugador se guarda codificada en base de datos, en vez de en texto plano, como hasta ahora; la API Rest se ejecuta mediante HTTP seguro; y a los sockets se les añade una capa de seguridad SSL. Los vemos por separado

### Codificación de la contraseña del jugador en la base de datos del sistema

Hemos decidido codificar la contraseña en base de datos mediante una función hash `sha256`. Además, la contraseña no va a ir sola, sino que se le añade una sal de 32 caracteres alfanuméricos. Esta sal se almacena en base de datos, en cada uno de los jugadores. Por último, la función hash se ejecuta dos veces, para tener algo más de seguridad frente a ataques de diccionario.  
La función hash utilizada está incluida en la librería hashlib de python, y la invocamos mediante ``pbkdf2_hmac('sha256', plaintext.encode(), salt.encode(), 2)``

Es importante destacar que esta función de hash debe ejecutarse tanto en el módulo Registry, a la hora de registrar/actualizar un usuario, como en el módulo Engine, cuando el usuario se conecta a una partida.

Como detalle de implementación, hemos creado un método ``getSalt()``, que recupera de la base de datos la sal del usuario indicado. Y en caso de no existir, crea una nueva sal.

### Conversión de la API rest (http) en API rest segura (https)

Hemos decidido realiza esta securización mediante codificación asimétrica, consistente en añadir los certificados SSL a la API. Nos hemos decantado por esta solución, ya que es el método más utilizado actualmente, y a la vez es muy sencilla de implementar. La forma de hacerlo ha sido hacer los certificados público y privado del módulo Registry accesibles al código, y modificar tanto la creación del servidor, como las llamadas a la API.  
En la creación del servidor, le hemos indicado que iba a ser un servidor https, y le hemos aportado los certificados, de la siguiente forma: ``app.run(debug=False, port=8000, host="0.0.0.0", ssl_context=(registry_cert,registry_key))``.  
En la parte de las llamadas a la API, las url ahora pasa a ser ``https`` en lugar de ``http``.  
Con estos pequeños cambios, Flask se encarga de resolver las peticiones seguras y de realizar todo el negociado de certificados.

### Sockets seguros (SSL)

Para securizar los sockets también nos hemos decantado por la codificación asimétrica. Es un método igual de seguro que la simétrica, y muy fácil de implementar. El funcionamiento de los sockets seguros consiste en establecer una comunicación insegura al principio, para añadir después los certificados, y aunque los datos se pueden interceptar, estos van a ir codificados por los certificados.  
En la implementeción hemos tenido que cambiar algunas cosas en Registry y Player.
En Player, añadimos la capa segura a los sockets, mediante la instrucción de la librería SSL ``ssl_conn=ssl.wrap_socket(conn,ca_certs=registry_pem)``, donde registry_pem es la clave pública del Registry. Y el envío se datos se realiza a través de este socket seguro, dejando el inseguro simplemente para establecer la conexión.  
En Registry realizamos algo similar. El socket seguro se encapsula dentro del socket inseguro con la instrucción de la librería SSL ``ssl_socket=ssl.wrap_socket(c,server_side=True,certfile=registry_cert,keyfile=registry_key, ssl_version=ssl.PROTOCOL_TLSv1_2)``, donde se le indica que está en el lado del servidor, y las claves pública y privada de Registry, además del protocolo que se va a utilizar.

## API_Engine

## Front

# Requirements

Install [docker](https://www.docker.com/products/docker-desktop/)

# Despliegue

En el despliegue se ha hecho uso de los contenedores de Docker. Nos hemos encotrado con problemas al asignar IP's estáticas , ya que al estar definidas en ``docker-compose.yml`` , si un servicio se quiere escalar, no sería posible ya que estaría ocupando la misma dirección IP. Para solucionar esto, dejamos que Docker sea el que nos proporcione las direcciones, ya que al permitirnos crear una red interna, sus componentes se conectan al adaptador ``Docker 0`` , que actúa como un switch, y sería la puerta por defecto de nuestra red. Al no conocer las IP's que nos van a proporcionar a nuestros servicios, tenemos el problema de que no sabemos dónde conectarnos de un módulo cliente a un módulo servidor. Para ello, se ha hecho uso de scripts, que nos filtrarán las direcciones de cada contenedor desplegado. Tras usar ``docker compose up -d --scale aa_player=x`` , no nos tendríamos que preocupar de que un mismo servicio se tenga que conectar con una IP ya usada. El parámetro ``--scale`` nos permite escalar el número de instancias de un determinado servicio.
El despliegue quedaría de la siguiente manera:


<img src=files/images/docker.jpg width=400px height=400px>


Y lo desplegaríamos ejecutando desde el directorio ``/src`` lo siguiente:
`./run.sh`

## Correr servicios

#### AA_Engine
``./run_engine.sh``

#### AA_Weather
``./run_weather.sh``

#### AA_Registry
``./run_registry.sh``

#### AA_Player
``./run_player.sh``

#### AA_NPC
``./run_npc.sh``

#### API_Engine
``./run_api_engine.sh``

#### Front
``./run_front.sh``

## Parar servicios

``./stop.sh``

## Eliminar servicios

``./clean.sh``






