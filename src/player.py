from enum import Enum

from src.piece import PieceColor, PieceType

class PlayerType(Enum):
    HUMAN = 1
    ROBOT = 2

class Player:
    def __init__(self, color: PieceColor, time_left: float, robot=False):
        self.__color = color 
        self.score = 0
        self.time_left = time_left 
        self.piecesLeft = [p_type for p_type in  PieceType] + [PieceType.KNIGHT,PieceType.ROOK] + 7*[PieceType.PAWN]
        self.piecesCaptured = []
        self.type = PlayerType.ROBOT if robot else PlayerType.HUMAN

    @property
    def color(self):
        return self.__color

    def reset(self,time_left):
        """
        Reset player data back to how it should be in the beginning of the game.
        """
        self.score = 0
        self.piecesLeft = [p_type for p_type in  PieceType] + [PieceType.KNIGHT,PieceType.ROOK] + 7*[PieceType.PAWN]
        self.piecesCaptured = []
        self.time_left = time_left 

    def remove_piece(self, p_type: PieceType) -> None:
        try:
            self.piecesLeft.remove(p_type)
        except:
            pass

    def add_piece(self, p_type: PieceType) -> None:
        self.piecesLeft.append(p_type)

    def remove_captured_piece(self) -> None:
        try:
            self.piecesCaptured.pop()
        except:
            pass

    def add_captured_piece(self, p_type: PieceType | None) -> None:
        if(p_type):
            self.piecesCaptured.append(p_type)


