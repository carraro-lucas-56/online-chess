from src.piece import PieceColor, PieceType
from enum import Enum

class Player:
    def __init__(self, color: PieceColor):
        self.__color = color 
        self.score = 0
        self.piecesLeft = [p_type for p_type in  PieceType] + [PieceType.KNIGHT,PieceType.ROOK] + 7*[PieceType.PAWN]

    @property
    def color(self):
        return self.__color

    def remove_piece(self, p_type: PieceType) -> None:
        self.piecesLeft.remove(p_type)

    def add_piece(self, p_type: PieceType) -> None:
        self.piecesLeft.append(p_type)

