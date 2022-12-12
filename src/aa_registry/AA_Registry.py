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
from datetime import datetime, time
import logging

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
        logging.info(BD_CONNECTION)
        print(BD_CONNECTION)
    except:  
        print(BD_ERR)
        logging.error(BD_ERR)
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
def inserting(c, address):
    c.send('Inserting...'.encode())
    dataReceived = c.recv(1024).decode()
    # recoge los datos del usuario y los convierte a json
    dataJson = json.loads(dataReceived)
    ip = address[0]

    if mongoInsert(dataJson):
        logging.info(ip + " [INSERT][SOCKET] Nuevo cliente insertado correctamente.")
        c.send('Inserted succesfully !'.encode())
    else:
        logging.error(ip + " [INSERT][SOCKET] Error al insertar nuevo cliente.")
        c.send('Error while inserting !'.encode())

# Opción de actualizar en la base de datos
def updating(c, address):
    c.send('Updating...'.encode())

    dataReceived = c.recv(1024).decode()
    oldData = json.loads(dataReceived)
    c.send('Old data received !'.encode())

    dataReceived = c.recv(1024).decode()
    newData = json.loads(dataReceived)
    #c.send('New data received !'.encode())
    ip = address[0]
            
    if mongoUpdate(oldData, newData):
        logging.info(ip + " [UPDATE][SOCKET] Actualizacion de datos de cliente correcta.")
        c.send('Updated succesfully !'.encode())
    else:
        logging.error(ip + " [UPDATE][SOCKET] Error al actualizar los datos de cliente ")
        c.send('Error while updating !'.encode())

@app.route('/registrar', methods = ['POST'])
def registrar():
    
    data = request.args.get('data')
    ip = request.remote_addr
    dataJson = json.loads(data)
    
    if mongoInsert(dataJson):
        logging.info(ip + " [INSERT][API] Nuevo cliente insertado correctamente.")
        return ('Inserted succesfully !')
    else:
        logging.error(ip + " [INSERT][API] Error al insertar nuevo cliente.")
        return ('Error while inserting !')

@app.route('/actualizar', methods = ['POST'])
def actualizar():
    
    data = request.args.get('oldData')
    ip = request.remote_addr
    oldData = json.loads(data)
    data = request.args.get('newData')
    newData = json.loads(data)
    
    if mongoUpdate(oldData, newData):
        logging.info(ip + " [UPDATE][API] Actualizacion de datos de cliente correcta.")
        return ('Updated succesfully !')
    else:
        logging.error(ip + " [UPDATE][API] Error al actualizar los datos de cliente ")
        return ('Error while updating !')        

def apiRun():
    try:
        logging.debug("Arrancando servidor registro API")
        app.run(debug=False, port=8000, host="0.0.0.0")
        logging.debug("Servidor registro API arrancado correctamente")
    except Exception as ex:
        logging.critical(str(ex))

def socketRegistry():
    
    AA_Registry = Modulo('AA_Registry')

    try:
        logging.debug("Arrancando servidor registro socket")
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
            logging.debug("[SOCKET] Connection from: " + str(address))  
            print("[SOCKET] Connection from: " + str(address))

            # decodifica los datos enviados para que se puedan leer y procesar
            option = c.recv(1024).decode()
            if option == 'insert':
                inserting(c, address)

            elif option == 'update':
                updating(c, address)

            c.close()
            logging.debug("[SOCKET] Closed connection: " + str(address))  
            print('[SOCKET] Closed connection: ' + str(address))
    except Exception as ex:  
        logging.critical(str(ex))      

def main():

    nombreFecha = datetime.now().strftime('registry_%Y%m%d.log')
    #Configuro el sistema de logging
    logging.basicConfig(filename=nombreFecha, filemode="a", level=logging.DEBUG, format='%(levelname)s %(asctime)s: %(message)s')
    logging.getLogger('werkzeug').disabled = True
    logging.debug("Aplicación iniciada")
    

    t1 = threading.Thread(target=socketRegistry, args = [])
    t2 = threading.Thread(target=apiRun, args = [])
    t1.start()
    t2.start()
    t1.join()
    t2.join()


if __name__ == "__main__":
    main()