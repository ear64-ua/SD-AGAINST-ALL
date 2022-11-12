from base64 import encode
from kafka import KafkaProducer
from kafka import KafkaConsumer
from classes import Modulo
from time import sleep
from json import dumps
from json import loads
from threading import Thread
import random

alias = ''
numJugador = ''
jugadorVivo = True
partidaIniciada = True
arrayMovimientos = ['N','S','E','W','NW','NE','SE','SW']

def leerMapa(Broker):
    global jugadorVivo
    global partidaIniciada

    consumer = KafkaConsumer(
    'mapa',
     bootstrap_servers=[f'{Broker.getIp()}:{Broker.getPort()}'],
     auto_offset_reset='latest',
     enable_auto_commit=True,
     value_deserializer=lambda x: loads(x.decode('utf-8')))

    for message in consumer:
        if(jugadorVivo):
            message = message.value

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

def insertarMovimiento(Broker):
    global jugadorVivo
    global partidaIniciada
    producer = KafkaProducer(bootstrap_servers=[f'{Broker.getIp()}:{Broker.getPort()}'],
                         value_serializer=lambda x: 
                         dumps(x).encode('utf-8'))

    while True:
        indice = random.randint(0,len(arrayMovimientos)-1)
        data = {'alias': alias,
                'codigoPartida' : 'NPC',
                'move' : arrayMovimientos[indice]}
        print(data)               
        if(jugadorVivo):        
            producer.send('player_move', value=data)
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
     value_deserializer=lambda x: loads(x.decode('utf-8')))

    for message in consumer:
        message = message.value 
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

    global alias

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