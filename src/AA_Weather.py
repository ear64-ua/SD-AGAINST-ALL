import json
import random

MAX_CITIES = 10

def chooseCities(data):

    cities = []
    i = 0
    while i < 4:

        indx = random.randint(0,MAX_CITIES-1)
        if data['ciudades'][indx] not in cities:
            cities.append(data['ciudades'][indx])
            i += 1            

    return cities


def main():

    file = open('data.json')

    data = json.load(file)

    print(chooseCities(data))


    file.close()


if __name__ == '__main__':
    main()