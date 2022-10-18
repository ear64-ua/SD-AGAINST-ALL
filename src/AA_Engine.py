import json
import random
import socket
import sys
from AA_Player import Modulo

VACIO = '*'
TAM_CIUDAD = 10
TAM_TABLERO = 20
MIN_ALIMENTOS = 15
MAX_ALIMENTOS = 25
MAX_MINAS = 25
MIN_MINAS = 15

class Ciudad:
    def __init__(self,nombre,temperatura,tam):
        self.nombre = nombre
        self.temperatura = temperatura
        self.alimentos = random.randint(MIN_ALIMENTOS,MAX_ALIMENTOS)
        self.minas = random.randint(MIN_MINAS,MAX_MINAS)
        self.tam = tam

    def getNombre(self):
        return self.nombre

class Mapa:

    def __init__(self, tam):
        self.tam = tam
        self.ciudades = []
        
    def addCiudad(self,ciudad):
        self.ciudades.append(ciudad)

    def __str__(self):

        c = '       '
        c += self.ciudades[0].getNombre()
        c+=('\t\t\t  ')
        c += self.ciudades[1].getNombre()

        c += '\n       '
        for i in range(21):
            if i == 0:
                continue
            c += str(i)
            if i < 10:
                c +='  '
            else: 
                c+=' '

        c += '\n'
        c += '    '

        for i in range(21):
            c += '#  '
        c += '\n'

        num_fila = 0
        columna = 0
        indx = 0

        # recorremos por cada fila, dos ciudades e imprimimos sus valores
        for bloque in range(2):

            for fila in range(10):
                c += str(num_fila+1)
                if num_fila+1 < 10:
                    c +=' '
                c += '  #  '

                # agarramos las dos ciudades
                for ciudad in  self.ciudades[indx:indx+2]:
                    for i in range(10):
                        c += VACIO
                        c += '  '
                 

                num_fila += 1
                
                c += '\n'

            # pasamos a las siguientes ciudades
            indx += 2
                 
        c += '       '
        c += self.ciudades[2].getNombre()
        c+=('\t\t\t  ')
        c += self.ciudades[3].getNombre()

        return c



def main():

    mapa = Mapa(TAM_TABLERO)
    cities = ''
    file = open('player_args.json')

    data = json.load(file)

    # guardar el puerto e IP de weather
    AA_Weather = Modulo()
    for dir in data['direcciones']:
        if data['Id'] == 'AA_Weather':
            AA_Weather.setIp(dir['IP'])
            AA_Weather.setPort(dir['port'])

    try:
        conn = socket.socket()
    except socket.error as err:
        print('Socket error because of %s' %(err))

    try:
        conn.connect((AA_Weather.getIp(), AA_Weather.getPort()))

        # enviar peticion
        conn.send('send cities'.encode())

        # espera de ciudades
        cities = conn.recv(1024).decode()
        print(cities)
       
    except socket.gaierror:
        print('There an error resolving the host')
        sys.exit() 
                
    conn.close()


    # lee las ciudades almacenadas en el fichero y las añade al mapa
    for ciudad in cities:
        nueva_ciudad=Ciudad(ciudad['nombre'],ciudad['temperatura'],TAM_CIUDAD)
        mapa.addCiudad(nueva_ciudad)

    print(mapa)

    file.close()






if __name__ == "__main__":
    main()

    