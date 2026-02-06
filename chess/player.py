from enum import Enum
from .piece import PieceColor, PieceType, Piece
import numpy as np

class PlayerType(Enum):
    HUMAN = 1
    ROBOT = 2

class Player:
    def __init__(self, color: PieceColor, time_left: float, board: np.array,robot=False):
        self.__color = color 
        self.score = 0
        self.time_left = time_left 
        self.piecesLeft = [piece for piece in board.flat if piece and piece.color == color]
        self.piecesCaptured = []
        self.type = PlayerType.ROBOT if robot else PlayerType.HUMAN

    @property
    def color(self):
        return self.__color

    def reset(self,board: np.array, time_left: float) -> None:
        """
        Reset player data back to how it should be in the beginning of the game.
        """
        self.score = 0
        self.piecesLeft = [piece for piece in board.flat if piece and piece.color == self.color]
        self.piecesCaptured = []
        self.time_left = time_left 

    def remove_piece(self, piece: Piece) -> None:
        try:
            self.piecesLeft.remove(piece)
        except:
            pass

    def add_piece(self, piece: Piece) -> None:
        self.piecesLeft.append(piece)

    def remove_captured_piece(self) -> None:
        try:
            self.piecesCaptured.pop()
        except:
            pass

    def add_captured_piece(self, piece: Piece | None) -> None:
        if(piece):
            self.piecesCaptured.append(piece)


