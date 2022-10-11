import sys
import socket
import json

def main():

    if len(sys.argv) != 2:
        print('ERROR en argumentos. Uso: fichero puerto_escucha')
        return
    
    host = socket.gethostname()
    port = 1500 #sys.argv[1]

    register_socket = socket.socket() 
    register_socket.bind((host, port))  

    register_socket.listen(4)

    print(f'Waiting for someone to register...{[host,port]} ')

    while(True):

        c, address = register_socket.accept()  
        print("Connection from: " + str(address))

        dataReceived = c.recv(1024).decode()

        dataJson = json.loads(dataReceived)

        alias = dataJson['alias']
        password = dataJson['password']
        nivel = dataJson['nivel']
        ef = dataJson['ef']
        ec = dataJson['ec']

        print(alias)
        print(password)
        print(nivel)
        print(ef)
        print(ec)

        c.close()




if __name__ == "__main__":
    main()