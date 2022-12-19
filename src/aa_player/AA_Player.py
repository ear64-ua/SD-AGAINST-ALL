from base64 import encode
import base64
import os
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
import requests
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes, padding, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import ssl
import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)

alias = ''
password = ''
codigoPartida = 0
jugadorVivo = True
partidaIniciada = False
numMovimientos = 1
ackRecibido = True
registry_pem = "secrets/registry.pem"
engine_pem = "secrets/cert.pem"

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
        enable_auto_commit=True
    )

    for message in consumer:
        if(jugadorVivo):
            message = loads(message.value.decode('utf-8'))
        
            base64salt = base64.b64decode(message['salt'])
            base64password = base64.b64decode(message['password'])

            message = desencryptMessage(
                base64.b64decode(message['message']).decode('utf-8'),
                base64salt,
                base64password
            )

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

def getPublicKey():

    with open("/secrets/engine/public_key.pem", "rb") as key_file:
      # Read the contents of the file into a variable
      key_data = key_file.read()
      # Do something with the key data, such as loading it as a public key
      public_key = serialization.load_pem_public_key(
        key_data, 
        backend=default_backend()
      )

    return public_key

def encryptMessage(message, salt, password):

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000
    )

    aes_key = base64.urlsafe_b64encode(kdf.derive(password))
    # Create a Fernet object using the AES key
    fernet = Fernet(aes_key)
    
    # Encypt message
    message_bytes = bytes(message, 'utf-8')
    encrypted_message = fernet.encrypt(message_bytes)

    return encrypted_message

def insertarMovimiento(Broker):
    global jugadorVivo
    global numMovimientos
    global partidaIniciada
    global ackRecibido

    producer = KafkaProducer(bootstrap_servers=[f'{Broker.getIp()}:{Broker.getPort()}'])

    while True:

        public_key = getPublicKey()
        #private_key = getPrivateKey()

        salt = os.urandom(16)
        password=b"password"

        encrypted_salt = public_key.encrypt(
            salt,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        encrypted_password = public_key.encrypt(
            password,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        message = {
            'alias': alias,
            'codigoPartida' : codigoPartida,
            'numMovimiento' : numMovimientos,
            'move' : input()
        }

        # encrypt message
        encrypted_message = encryptMessage(dumps(message),salt,password)

        # define encrypted structure
        data = {
            'message' : base64.b64encode(encrypted_message).decode('utf-8'),
            'salt' : base64.b64encode(encrypted_salt).decode('utf-8'),
            'password' : base64.b64encode(encrypted_password).decode('utf-8')
        }

        if(jugadorVivo and partidaIniciada):        
            producer.send('player_move', value=dumps(data).encode('utf-8'))
            numMovimientos = numMovimientos + 1
            ackRecibido = False    
        sleep(1)
        if(not(ackRecibido)):
            print('EL SERVIDOR SE HA CAIDO. POR FAVOR, ESPERA A LA RECONEXION')
            partidaIniciada = False

        if(not(jugadorVivo)):
            producer.close()
            return


def desencryptMessage(encrypted_message,encrypted_salt,encrypted_password):

    with open("/secrets/engine/private_key.pem", "rb") as key_file:
        private_key = serialization.load_pem_private_key(
            key_file.read(),
            password=None,
            backend=default_backend()
        )

    salt = private_key.decrypt(
            encrypted_salt,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
    #print(f'decrypted salt: {salt}')

    password = private_key.decrypt(
            encrypted_password,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
    #print(f'decrypted password: {password}')

     # Generate the AES key using PBKDF2 HMAC
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000
    )
    
    aes_key = base64.urlsafe_b64encode(kdf.derive(password))
        
    # Create a Fernet object using the AES key
    fernet = Fernet(aes_key)

    # Decrypt the message using Fernet
    decrypted_message = fernet.decrypt(encrypted_message)

    #print(f'decrypted message: {decrypted_message}')

    return loads(decrypted_message.decode('utf-8'))

def leerEstado(Broker):

    global jugadorVivo
    global numMovimientos
    global partidaIniciada
    global ackRecibido

    consumer = KafkaConsumer(
        'estadoJugador',
        bootstrap_servers=[f'{Broker.getIp()}:{Broker.getPort()}'],
        auto_offset_reset='latest',
        enable_auto_commit=True
    )

    for message in consumer:
        message = loads(message.value.decode('utf-8'))
        
        base64salt = base64.b64decode(message['salt'])
        base64password = base64.b64decode(message['password'])

        #print(f'base 64 salt {base64salt}')
        #print(f'base 64 password {base64password}')

        #print(base64.b64decode(message['message']).decode('utf-8'))

        message = desencryptMessage(
            base64.b64decode(message['message']).decode('utf-8'),
            base64salt,
            base64password
        )

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
    try:
        ssl_engine_socket = ssl.wrap_socket(engine_socket,ca_certs=engine_pem)
        # usamos el nombre de host y lo pasamos a IP para que se conecte al socket
        ssl_engine_socket.connect((AA_Engine.getIp(),AA_Engine.getPort()))

        msg = ssl_engine_socket.recv(1024).decode() 

        print(msg)

        global alias
        alias = input('alias: ')
        password = input('password: ')

        login = {   'alias' : alias,
                    'password' : password
                }

        login = json.dumps(login)

        ssl_engine_socket.send(login.encode())

        data = ssl_engine_socket.recv(1024).decode()
        data = json.loads(data)

        print(data['msg'])
        print()

        if data['verified']:
            codigoPartida = data['codigoPartida']    
            conectado = True

        ssl_engine_socket.close()
        engine_socket.close()    

    except Exception as e:
        print(e)

    return conectado

def insertRegistrySocket(AA_Registry):

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
        ssl_conn = ssl.wrap_socket(conn, ca_certs=registry_pem)
    except socket.error as err:
        print('Socket error because of %s' %(err))
    except Exception as e:
        print(e)    

    try:
        ssl_conn.connect((AA_Registry.getIp(), AA_Registry.getPort()))

        # notificamos al servidor que se quiere insertar
        ssl_conn.send('insert'.encode())
        msg = ssl_conn.recv(1024).decode()
        print(msg)

        # mandamos los datos al servidor
        ssl_conn.send(datos.encode())
        msg = ssl_conn.recv(1024).decode()
        print(msg)
        print()

    except socket.gaierror:
        print('There an error resolving the host')
        sys.exit() 
    except Exception as e:
        print(e)
        sys.exit()    
                
    ssl_conn.close()            
    conn.close()

# Conecta con la base de datos y devuelve si se ha insertado o no
def updateRegistrySocket(AA_Registry):

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
        ssl_conn = ssl.wrap_socket(conn, ca_certs=registry_pem)
    except socket.error as err:
        print('Socket error because of %s' %(err))
    except Exception as e:
        print(e)  

    try:
        ssl_conn.connect((AA_Registry.getIp(), AA_Registry.getPort()))

        # send action to server
        ssl_conn.send('update'.encode())
        msg = ssl_conn.recv(1024).decode()
        print(msg)

        ssl_conn.send(oldData.encode())
        msg = ssl_conn.recv(1024).decode() # confirmación de datos antiguos

        ssl_conn.send(newData.encode())
        msg = ssl_conn.recv(1024).decode() # confirmación de insert
        print(msg)
        print()
       
    except socket.gaierror:
        print('There an error resolving the host')
        sys.exit() 
    except Exception as e:
        print(e)
        sys.exit()    
                
    ssl_conn.close()                
    conn.close()

def insertRegistryApi(registry):
    
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

    ip = registry.getIp()

    api_request = 'https://' + ip + ':8000' + '/registrar?data=' + datos

    requests.packages.urllib3.disable_warnings()
    response = requests.post(api_request, verify=False)
    data = response.text
    print(data)

def updateRegistryApi(registry):
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

    ip = registry.getIp()

    api_request = 'https://' + ip + ':8000' + '/actualizar?oldData=' + oldData + '&newData=' + newData

    requests.packages.urllib3.disable_warnings()
    response = requests.post(api_request, verify=False)
    data = response.text
    print(data)

# Muestra el menú de opciones que tiene el jugador
def menu2():

    print('Elige una opción:')
    print('1. Crear perfil')
    print('2. Editar perfil')
    print('3. Unirse a partida')
    print('4. Salir')

    return input('Tu opción: ')


def menu():
    print('Elige tu forma de conexion al juego:')
    print('1. Sockets')
    print('2. Api Rest')
    print('3. Salir')

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

    opcion = '0'

    while jugadorVivo:
        if (opcion != '1' and opcion != '2'):
            opcion = menu()
        if opcion == '1':
            opcionS = menu2()
            if opcionS == '1': # Creamos un usuario
                insertRegistrySocket(AA_Registry)
            elif opcionS == '2': # Editamos la contraseña del usuario
                updateRegistrySocket(AA_Registry)
            elif opcionS == '3': # Conexión a partida
                if conectarPartida(AA_Engine):
                    jugarPartida(Broker)
            else:
                break        
        elif opcion == '2':
            opcionAR = menu2()
            if opcionAR == '1': # Creamos un usuario
                insertRegistryApi(AA_Registry)
            elif opcionAR == '2': # Editamos la contraseña del usuario
                updateRegistryApi(AA_Registry)
            elif opcionAR == '3': # Conexión a partida
                if conectarPartida(AA_Engine):
                    jugarPartida(Broker)
            else:
                break
        elif opcion == '3':
            break
        else:
            continue

    

if __name__ == "__main__":
    main()