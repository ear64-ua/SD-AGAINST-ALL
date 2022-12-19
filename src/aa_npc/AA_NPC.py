from base64 import encode
import os
from kafka import KafkaProducer
from kafka import KafkaConsumer
from classes import Modulo
from time import sleep
from json import dumps
from json import loads
from threading import Thread
import random
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes, padding, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes


alias = ''
nivel = 1
numJugador = ''
jugadorVivo = True
partidaIniciada = True
arrayMovimientos = ['N','S','E','W','NW','NE','SE','SW']


def desenryptMessage(encrypted_message,encrypted_salt,encrypted_password):

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


def leerMapa(Broker):
    global jugadorVivo
    global partidaIniciada

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

            message = desenryptMessage(
                base64.b64decode(message['message']).decode('utf-8'),
                base64salt,
                base64password
            )

            if('mapa' in message):
                mapa = message['mapa']
                print(mapa)
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
    global partidaIniciada

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

        indice = random.randint(0,len(arrayMovimientos)-1)
        message = {
            'alias': alias,
            'codigoPartida':    'NPC',
            'move' :            arrayMovimientos[indice],
            'nivel':            nivel
        }

        # encrypt message
        encrypted_message = encryptMessage(dumps(message),salt,password)

        # define encrypted structure
        data = {
            'message' : base64.b64encode(encrypted_message).decode('utf-8'),
            'salt' : base64.b64encode(encrypted_salt).decode('utf-8'),
            'password' : base64.b64encode(encrypted_password).decode('utf-8')
        }
        
        print(message)               
        
        if(jugadorVivo):        
            producer.send('player_move', value=dumps(data).encode('utf-8'))
        sleep(5)

        if(not(jugadorVivo)):
            producer.close()
            return

def leerEstado(Broker):

    global jugadorVivo
    global partidaIniciada

    consumer = KafkaConsumer(
        'estadoJugador',
        bootstrap_servers=[f'{Broker.getIp()}:{Broker.getPort()}'],
        auto_offset_reset='latest',
        enable_auto_commit=True,
    )

    for message in consumer:
        message = loads(message.value.decode('utf-8'))
        
        base64salt = base64.b64decode(message['salt'])
        base64password = base64.b64decode(message['password'])

        message = desenryptMessage(
            base64.b64decode(message['message']).decode('utf-8'),
            base64salt,
            base64password
        )
        print(message)

        if(message['alias'] == alias and partidaIniciada):
            if(message['nivelReal'] == -99):
                print('HAS MUERTO')
                jugadorVivo = False
        if (message['alias'] == 'broadcast'):
            if (message['estadoPartida'] == 'inicioPartida'):
                print('LA PARTIDA HA COMENZADO')
                partidaIniciada = True
            elif (message['estadoPartida'] == 'finPartida'):
                if(partidaIniciada):
                    print('FIN DE LA PARTIDA')
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

    global alias,nivel

    nivel = random.randint(1,9)
    seed = random.randint(0,999999999)
    alias = str(nivel) + 'NPC_' + str(seed)

    t1 = Thread(target=insertarMovimiento, args = [Broker])
    t2 = Thread(target=leerMapa, args = [Broker])
    t3 = Thread(target=leerEstado, args = [Broker])
    t1.start()
    t2.start()
    t3.start()
    t1.join()
    t2.join()
    t3.join()

def main():
    
    # Creamos los módulos para conseguir las direcciones necesarias
    Broker = Modulo('Broker') 

    while jugadorVivo:
        print('Comienza la partida')
        jugarPartida(Broker)

    

if __name__ == "__main__":
    main()