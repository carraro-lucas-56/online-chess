import socket
import pickle
import os
import logging
import queue
import threading
from dotenv import load_dotenv

from chess.piece import Move, PieceColor

logger = logging.getLogger(__name__)

load_dotenv()
SERVER_IP = os.getenv("SERVER_IP")

class Network():
    def __init__(self):
        self.client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.server = SERVER_IP
        self.port = 5555
        self.addr = (self.server,self.port)
        self.thread = None
        self.thinking = threading.Event()
        self.stop_event = threading.Event()
        self.queue = queue.Queue()

    def connect(self) -> None:
        try:
            self.client.connect(self.addr)
            logger.info("Connected to the server")
        except socket.error as e:
            logger.error(f"Error {e} when connecting to the server")

    def send(self, data) -> None:
        try:
            if data:
                self.client.send(pickle.dumps(data))
        except socket.error as e:
            logger.error(f"Error {e} when sending data to the server")
    
    def receive(self) -> Move | PieceColor | bool:
        try:
            return pickle.loads(self.client.recv(2048))
        except socket.error as e:
            logger.error(f"Error {e} when receiving data from the server")
    
    def threaded_receive(self) -> Move | PieceColor | bool:
        try:
            self.queue.put(pickle.loads(self.client.recv(2048)))
        except socket.error as e:
            logger.error(f"Error {e} when receiving data from the server")
    
    def send_and_receive(self, data) -> Move | PieceColor | bool:
        self.send(data)
        return self.receive()    

    def start_receive_thread(self):
        self.thread = threading.Thread(target=self.threaded_receive,
                                       args=[],
                                       daemon=True)
        self.thread.start()

    def start_thread(self, lastMove: Move | None = None) -> None:
        self.thread = threading.Thread(target=self.get_move,
                                       args=[lastMove],
                                       daemon=True)
        self.thread.start()

    def get_move(self, lastMove: Move | None = None) -> None:
        self.thinking.set()
    
        try:
            if self.stop_event.is_set():
                return

            opp_move = self.send_and_receive(lastMove)
            self.queue.put(opp_move)

            if self.stop_event.is_set():
                return
        except Exception as e:
            logger.error(f"Network thread crashed due to {e}")
        finally:
            self.thinking.clear()
