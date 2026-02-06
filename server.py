import socket
import pickle
import random
import os
from dotenv import load_dotenv

from chess.piece import PieceColor, Move

load_dotenv()
SERVER_IP = os.getenv("SERVER_IP")

s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

server = SERVER_IP
port = 5555

try:
    s.bind((server,port))
except socket.error as e:
    print(str(e))

s.listen(2)
print("Server wating for connections")

while True:
    x = random.randint(1,2)
    
    conn, addr = s.accept()
    print(f"connected to {addr}")
    
    conn.send(pickle.dumps(PieceColor(x)))

    conn2, addr = s.accept()
    print(f"connected to {addr}")
    
    conn2.send(pickle.dumps(PieceColor(1 if x == 2 else 2)))

    (white,black) = (conn,conn2) if x == 1 else (conn2,conn) 

    move = pickle.loads(white.recv(2048))
    
    while True:
        try:
            black.send(pickle.dumps(move))
            move = pickle.loads(black.recv(2048))

            white.send(pickle.dumps(move))
            move = pickle.loads(white.recv(2048))
        except Exception as e:
            print(str(e))
            white.close()
            black.close()
            break

    

    