import json
import random
import socket

from classes import Modulo

MAX_CITIES = 10

# Elige las NUM_CITIES ciudades que se establecerán en la partida
def chooseCity():

    file = open('json_files/data.json')
    data = json.load(file)
    file.close()

    indx = random.randrange(0,MAX_CITIES) 

    return data['ciudades'][indx]

def main():

    AA_Weather =  Modulo('AA_Weather')

    # inicializamos el socket
    conn = socket.socket() 
    ip = socket.gethostbyname_ex(AA_Weather.getIp())[2][0]
    conn.bind((ip, AA_Weather.getPort())) 

    conn.listen(2)

    print(f' AA_Weather listening for AA_Engine petition...{[ip,AA_Weather.getPort()]} ')

    while True:
        engine, address = conn.accept()  
        peticion = ''
        # si se envía una ciudad repetida, se vuelve a enviar otra
        while peticion != 'ok':
            peticion = engine.recv(1024).decode()
            print("Petition received from: " + str(address) + '-> ' + peticion )
            city = json.dumps(chooseCity())
            engine.send(city.encode())

if __name__ == '__main__':
    main()