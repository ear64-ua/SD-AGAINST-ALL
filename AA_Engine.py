import json

def main():
    file = open('data.json')

    data = json.load(file)

    for i in data['ciudades']:
        print(i['nombre'])

    file.close()

if __name__ == "__main__":
    main()

    