from ast import alias
import sys
import socket
import json
from pymongo import MongoClient   

def mongoConnect(data):
 
    try:
        conn = MongoClient()
        print("Connected successfully!!!")
    except:  
        print("Could not connect to MongoDB")

    db = conn.gameDB

    collection = db.players

    collection.insert_one(data)


def main():

    if len(sys.argv) != 2:
        print('ERROR en argumentos. Uso: fichero puerto_escucha')
        return
    
    host = socket.gethostname()
    port = int(sys.argv[1])

    # inicializamos el socket
    register_socket = socket.socket() 
    register_socket.bind((host, port)) 

    # puede escuchar hasta a 4 jugadores
    register_socket.listen(4)

    print(f'Waiting for someone to register...{[host,port]} ')

    while(True):

        # conectamos con el cliente
        c, address = register_socket.accept()  
        print("Connection from: " + str(address))

        # decodifica los datos enviados para que se puedan leer y procesar
        dataReceived = c.recv(1024).decode()

        # recoge los datos del usuario y los convierte a json
        dataJson = json.loads(dataReceived)

        mongoConnect(dataJson)

        c.close()




if __name__ == "__main__":
    main()