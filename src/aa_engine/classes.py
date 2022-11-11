import json

class Modulo:
    
    def __init__(self,id):

        file = open('json_files/addresses.json')
        data = json.load(file)
        file.close()

        for dir in data['direcciones']:
            if dir['Id'] == id:
                self.ip = dir['IP']
                self.port = int(dir['port'])

    def setIp(self,ip):
        self.ip = ip
    
    def setPort(self,port):
        self.port = port
    
    def getIp(self):
        return self.ip
    
    def getPort(self):
        return self.port