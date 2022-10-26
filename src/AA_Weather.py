import json
import random
import socket

from AA_Player import Modulo

MAX_CITIES = 10

# Elige las NUM_CITIES ciudades que se establecerán en la partida
def chooseCity():

    file = open('src/json_files/data.json')
    data = json.load(file)
    file.close()

    indx = random.randrange(0,MAX_CITIES) 

    return data['ciudades'][indx]

def main():

    AA_Weather =  Modulo('AA_Weather')

    # inicializamos el socket
    conn = socket.socket() 
    conn.bind((AA_Weather.getIp(), AA_Weather.getPort())) 

    conn.listen(2)

    print(f' AA_Weather listening for AA_Engine petition...{[AA_Weather.getIp(),AA_Weather.getPort()]} ')

    while True:
        engine, address = conn.accept()  
        peticion = ''
        while peticion != 'ok':
            peticion = engine.recv(1024).decode()
            print("Petition received from: " + str(address) + '-> ' + peticion )
            city = json.dumps(chooseCity())
            engine.send(city.encode())
        #    

        #    peticion = engine.recv(1024).decode()
        #    print(peticion)
        #    city=str(chooseCity())
        #    engine.send(city.encode())



if __name__ == '__main__':
    main()