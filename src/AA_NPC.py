import socket
import sys
import json
from AA_Player import Modulo

def conectarPartida():
    return

def readDirections(data, Broker):

    for addr in data['direcciones']:
        if addr['Id'] == 'Broker':
            Broker.setIp(addr['IP'])
            Broker.setPort(int(addr['port']))

def main():
    
    args = open('player_args.json')
    data = json.load(args)

    Broker = Modulo() 

    readDirections(data,Broker)

    conectarPartida()

    args.close()

    


    

if __name__ == "__main__":
    main()