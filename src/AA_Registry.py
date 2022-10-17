from ast import alias
import sys
import socket
import json
from pymongo import MongoClient   
import pymongo

# Busca si el alias de un jugador existe en la base de datos
def findPlayer(collection,data):

    try:
        result = collection.find_one(data)
        # Si no encuentra ninguno devuelve None
        if result == None:
            return False

    except pymongo.errors.PyMongoError as e:
        print(e)
        return False

    return True

# Inserta los datos del jugador en la base de datos
def mongoInsert(data):

    try:
        conn = MongoClient()
        print("Connected to MongoDB successfully!!!")
    except:  
        print("Could not connect to MongoDB")
        return False

    db = conn.gameDB
    collection = db.players

    # Si no ha encontrado a nadie con el mismo alias, inserta
    if findPlayer(collection,{'alias' : data['alias']}):
        return False

    try:
        collection.insert_one(data)

    except pymongo.errors.PyMongoError as e:
        print(e)
        return False

    print('Inserted!')
    return True

# Actualiza los datos del jugador en la base de datos
def mongoUpdate(oldData, newData):

    try:
        conn = MongoClient()
        print("Connected to MongoDB successfully!!!")
    except:  
        print("Could not connect to MongoDB")
        return False

    db = conn.gameDB
    collection = db.players

    try:
        # buscamos al jugador con el mismo alias y password, y actualizamos el password
        result = collection.find_one_and_update(
            {
                'alias': oldData['alias'],
                'password': oldData['password']
            },
            {'$set': { 
                'password':newData['password']
                }
            }
        ) 
        # si no se ha actualizado ningún registro, devuelve error
        if result == None or not result.matched_count > 0:
            return False

    except pymongo.errors.PyMongoError as e:
        print(e)
        return False

    print('Updated!')
    return True

# Opción de insertar en la base de datos
def inserting(c):
    c.send('Inserting...'.encode())
    dataReceived = c.recv(1024).decode()
    # recoge los datos del usuario y los convierte a json
    dataJson = json.loads(dataReceived)
    
    if mongoInsert(dataJson):
        c.send('Inserted succesfully !'.encode())
    else:
        c.send('Error while inserting !'.encode())

# Opción de actualizar en la base de datos
def updating(c):
    c.send('Updating...'.encode())

    dataReceived = c.recv(1024).decode()
    oldData = json.loads(dataReceived)
    c.send('Old data received !'.encode())

    dataReceived = c.recv(1024).decode()
    newData = json.loads(dataReceived)
    #c.send('New data received !'.encode())
            
    if mongoUpdate(oldData, newData):
        c.send('Updated succesfully !'.encode())
    else:
        c.send('Error while updating !'.encode())

def main():

    if len(sys.argv) != 2:
        print('ERROR en argumentos. Uso: fichero puerto_escucha')
        return
    
    host = '127.0.0.1'
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
        option = c.recv(1024).decode()
        if option == 'insert':
            inserting(c)

        elif option == 'update':
            updating(c)

        c.close()


if __name__ == "__main__":
    main()