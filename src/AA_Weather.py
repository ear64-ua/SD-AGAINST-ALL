import json
import random
import socket

from AA_Player import Modulo

MAX_CITIES = 10

def chooseCities(data):

    cities = []
    i = 0
    while i < 4:

        indx = random.randint(0,MAX_CITIES-1)
        if data['ciudades'][indx] not in cities:
            cities.append(data['ciudades'][indx])
            i += 1            

    print(cities)
    return cities


def main():

    file = open('player_args.json')

    data = json.load(file)

    # guardar el puerto e IP de weather
    AA_Weather = Modulo()
    for dir in data['direcciones']:
        if data['Id'] == 'AA_Weather':
            AA_Weather.setIp(dir['IP'])
            AA_Weather.setPort(dir['port'])

    # inicializamos el socket
    conn = socket.socket() 
    conn.bind((AA_Weather.getIp(), AA_Weather.getPort())) 

    peticion = conn.recv(1024).decode()
    conn.send(str(chooseCities(data)).encode())

    file = open('data.json')

    data = json.load(file)

    file.close()


if __name__ == '__main__':
    main()