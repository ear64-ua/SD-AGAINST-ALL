import json
import random
import socket
import sys


MAX_CITIES = 10

class Modulo:
    
    def __init__(self,id):
        self.ip = "127.0.0.1"
        file = open('json_files/addresses.json')
        data = json.load(file)
        file.close()

        for dir in data['direcciones']:
            if dir['Id'] == id:
                self.port = int(dir['port'])

    def setIp(self,ip):
        self.ip = ip
    
    def setPort(self,port):
        self.port = port
    
    def getIp(self):
        return self.ip
    
    def getPort(self):
        return self.port

# Elige las NUM_CITIES ciudades que se establecerán en la partida
def chooseCity():

    file = open('json_files/data.json')
    data = json.load(file)
    file.close()

    indx = random.randrange(0,MAX_CITIES) 

    return data['ciudades'][indx]

def main():

    if len(sys.argv[1:]) < 1:
        print('Uso incorrecto de argumentos. Use IP_Weather')
        return -1
    args = sys.argv[1:]

    AA_Weather =  Modulo('AA_Weather')
    AA_Weather.setIp(args[0])

    # inicializamos el socket
    conn = socket.socket() 
    conn.bind((AA_Weather.getIp(), AA_Weather.getPort())) 

    conn.listen(2)

    print(f' AA_Weather listening for AA_Engine petition...{[AA_Weather.getIp(),AA_Weather.getPort()]} ')

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