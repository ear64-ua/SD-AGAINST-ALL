import json
import random
import socket

from AA_Player import Modulo

MAX_CITIES = 10
NUM_CITIES = 4

# Elige las NUM_CITIES ciudades que se establecerán en la partida
def chooseCities():

    file = open('src/json_files/data.json')
    data = json.load(file)
    file.close()

    cities = []
    i = 0
    while i < NUM_CITIES:

        indx = random.randint(0,MAX_CITIES-1)
        if data['ciudades'][indx] not in cities:
            cities.append(data['ciudades'][indx])
            i += 1            

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

    c = json.dumps(c)

    return c


def main():

    AA_Engine =  Modulo('AA_Engine')

    chosenCities = chooseCities()

    # inicializamos el socket
    conn = socket.socket() 
    conn.bind((AA_Engine.getIp(), AA_Engine.getPort())) 

    conn.listen(1)

    print(f' AA_Weather listening for AA_Engine petition...{[AA_Engine.getIp(),AA_Engine.getPort()]} ')

    engine, address = conn.accept()  
    print("Petition received from: " + str(address))

    #while True:
    #    peticion = conn.recv(1024).decode()
    #    conn.send(str(chooseCities(chosenCities)).encode())



if __name__ == '__main__':
    main()