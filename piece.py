from enum import Enum
from abc import ABC, abstractmethod

class PieceColor(Enum):
    WHITE = 1
    BLACK = 2

class PieceType(Enum):
    PAWN = 1
    KNIGHT = 2
    BISHOP = 3
    ROOK = 4
    QUEEN = 5
    KING = 6

class PieceState(Enum):
    MOVED = 1
    NOT_MOVED = 2

class Piece(ABC):
    def __init__(self,
                 color: PieceColor,
                 type: PieceType,
                 position: tuple[int,int]):
        self.__color = color
        self.__type = type
        self.__state = PieceState.NOT_MOVED
        self.__value = self._piece_value(type)
        self.position = position

    def update_positiion(self, new_position: tuple[int,int]) -> None:
        self.postion = new_position

    @staticmethod
    def _piece_value(piece : PieceType) -> int:
        piece_value_dict = {
            "PAWN" : 1,
            "KNIGHT" : 3,
            "BISHOP" : 3,
            "ROOK" : 5,
            "QUEEN" : 10,
            "KING" : 1000
        }
        return piece_value_dict[piece.name]
    
    @property
    def color(self):
        return self.__color

    @property
    def value(self):
        return self.__value

    @property
    def type(self):
        return self.__type

    @property 
    def state(self):
        return self.__state

    @state.setter
    def state(self,new_state):
        # this conditon prevents setting a moved piece to not moved state
        if(self.state != PieceState.MOVED):
            self.__state = new_state

class Pawn(Piece):
    def __init__(self,
                 color: PieceColor,
                 position: tuple[int,int]):
        super().__init__(color,
                         PieceType.PAWN,
                         position)

class Knight(Piece):
    def __init__(self,
                 color: PieceColor,
                 position: tuple[int,int]):
        super().__init__(color,
                         PieceType.KNIGHT,
                         position)

class Bishop(Piece):
    def __init__(self,
                 color: PieceColor,
                 position: tuple[int,int]):
        super().__init__(color,
                         PieceType.BISHOP,
                         position)

class Rook(Piece):
    def __init__(self,
                 color: PieceColor,
                 position: tuple[int,int]):
        super().__init__(color,
                         PieceType.ROOK,
                         position)

class Queen(Piece):
    def __init__(self,
                 color: PieceColor,
                 position: tuple[int,int]):
        super().__init__(color,
                         PieceType.QUEEN,
                         position)
        
class King(Piece):
    def __init__(self,
                 color: PieceColor,
                 position: tuple[int,int]):
        super().__init__(color,
                         PieceType.KING,
                         position)
        