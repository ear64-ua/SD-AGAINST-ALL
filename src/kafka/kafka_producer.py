from time import sleep
from json import dumps
from kafka import KafkaProducer

producer = KafkaProducer(bootstrap_servers=['localhost:29092'],
                         value_serializer=lambda x: 
                         dumps(x).encode('utf-8'))


while True:
    data = {'move' : input('Choose your direction (E,W,S,N): ')}
    producer.send('player_move', value=data)
    sleep(5)