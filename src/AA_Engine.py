import json
import random

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

        for bloque in range(2):

            for fila in range(10):
                c += str(num_fila+1)
                if num_fila+1 < 10:
                    c +=' '
                c += '  #  '

                for ciudad in  self.ciudades[indx:indx+2]:
                    for i in range(10):
                        c += VACIO
                        c += '  '
                 

                num_fila += 1
                
                c += '\n'

            indx += 2
                 
        c += '       '
        c += self.ciudades[2].getNombre()
        c+=('\t\t\t  ')
        c += self.ciudades[3].getNombre()

        return c



def main():

    mapa = Mapa(TAM_TABLERO)

    file = open('src/data.json')

    data = json.load(file)

    for ciudad in data['ciudades']:
        nueva_ciudad=Ciudad(ciudad['nombre'],ciudad['temperatura'],TAM_CIUDAD)
        mapa.addCiudad(nueva_ciudad)

    file.close()

    print(mapa)


if __name__ == "__main__":
    main()

    