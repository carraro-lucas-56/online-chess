import socket
import pickle
import os
from dotenv import load_dotenv

load_dotenv()
SERVER_IP = os.getenv("SERVER_IP")

class Network():
    def __init__(self):
        self.client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.server = "192.168.15.106"
        self.port = 5555
        self.addr = (self.server,self.port)

    def connect(self):
        try:
            self.client.connect(self.addr)
            return pickle.loads(self.client.recv(2048))
        except socket.error as e:
            print(str(e))

    def send(self, data):
        try:
            if data:
                self.client.send(pickle.dumps(data))
            return pickle.loads(self.client.recv(2048))
        except socket.error as e:
            print(str(e))
