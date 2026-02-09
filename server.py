import socket
import pickle
import random
import os
import logging
from dotenv import load_dotenv

from chess.piece import PieceColor, Move

logger = logging.getLogger(__name__)

load_dotenv()
SERVER_IP = os.getenv("SERVER_IP")

s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

server = SERVER_IP
port = 5555

try:
    s.bind((server,port))
except socket.error as e:
    logger.error(f"Failed to bind socket")

s.listen(2)
logger.info("Server wating for connections")

while True:
    x = random.randint(1,2)
    
    conn, addr = s.accept()
    logger.info(f"connected to {addr}")
    
    conn.send(pickle.dumps(PieceColor(x)))

    conn2, addr = s.accept()
    logger.info(f"connected to {addr}")
    
    conn2.send(pickle.dumps(PieceColor(1 if x == 2 else 2)))

    (white,black) = (conn,conn2) if x == 1 else (conn2,conn) 

    move = pickle.loads(white.recv(2048))
    
    while True:
        try:
            black.send(pickle.dumps(move))
            move = pickle.loads(black.recv(2048))

            white.send(pickle.dumps(move))
            move = pickle.loads(white.recv(2048))
        
        except socket.error as e:
            logger.error(f"Game ended, client disconnected")

        except Exception:
            logger.exception("Unexpected error during game")

        finally:
            white.close()
            black.close()
            break

    

    