from ast import alias
from modulefinder import Module
import sys
import socket
import json
from pymongo import MongoClient   
import pymongo
from classes import Modulo
import threading
from flask import Flask, jsonify, request,send_file

app = Flask(__name__)

BD_CONNECTION = "[BD] Connected to MongoDB successfully!!!"
BD_ERR = "[BD] Could not connect to MongoDB"
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
        conn = MongoClient('mongodb://mongodb')
        print(BD_CONNECTION)
    except:  
        print(BD_ERR)
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

    print('[BD] Inserted!')
    conn.close()
    print('[BD] Closed')
    return True

# Actualiza los datos del jugador en la base de datos
def mongoUpdate(oldData, newData):

    try:
        conn = MongoClient('mongodb://mongodb')
        print(BD_CONNECTION)
    except:  
        print(BD_ERR)
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
        if result == None:
            return False

    except pymongo.errors.PyMongoError as e:
        print(e)
        return False

    print('[BD] Updated!')
    conn.close()
    print('[BD] Closed')
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

@app.route('/registrar', methods = ['POST'])
def registrar():
    
    data = request.args.get('data')
    dataJson = json.loads(data)
    
    if mongoInsert(dataJson):
        return ('Inserted succesfully !')
    else:
        return ('Error while inserting !')

@app.route('/actualizar', methods = ['POST'])
def actualizar():
    
    data = request.args.get('oldData')
    oldData = json.loads(data)
    data = request.args.get('newData')
    newData = json.loads(data)
    
    if mongoUpdate(oldData, newData):
        return ('Updated succesfully !')
    else:
        return ('Error while updating !')        

def apiRun():
    app.run(debug=False, port=8000, host="0.0.0.0")

def socketRegistry():
    
    AA_Registry = Modulo('AA_Registry')

    # inicializamos el socket
    register_socket = socket.socket() 
    ip = socket.gethostbyname_ex(AA_Registry.getIp())[2][0]
    register_socket.bind((ip, AA_Registry.getPort())) 

    # puede escuchar hasta a 4 jugadores
    register_socket.listen(4)

    print(f'[SOCKET] Waiting for someone to register...{[ip,AA_Registry.getPort()]} ')

    while(True):

        # conectamos con el cliente
        c, address = register_socket.accept()  
        print("[SOCKET] Connection from: " + str(address))

        # decodifica los datos enviados para que se puedan leer y procesar
        option = c.recv(1024).decode()
        if option == 'insert':
            inserting(c)

        elif option == 'update':
            updating(c)

        c.close()
        print('[SOCKET] Closed connection: ' + str(address))

def main():
    t1 = threading.Thread(target=socketRegistry, args = [])
    t2 = threading.Thread(target=apiRun, args = [])
    t1.start()
    t2.start()
    t1.join()
    t2.join()


if __name__ == "__main__":
    main()