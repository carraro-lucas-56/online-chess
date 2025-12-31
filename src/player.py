from src.piece import PieceColor, PieceType, Piece

class Player:
    def __init__(self, color: PieceColor, time_left: float):
        self.__color = color 
        self.score = 0
        self.time_left = time_left 
        self.piecesLeft = [p_type for p_type in  PieceType] + [PieceType.KNIGHT,PieceType.ROOK] + 7*[PieceType.PAWN]

    @property
    def color(self):
        return self.__color

    def reset(self,time_left):
        """
        Reset player data back to how it should be in the beginning of the game.
        """
        self.score = 0
        self.piecesLeft = [p_type for p_type in  PieceType] + [PieceType.KNIGHT,PieceType.ROOK] + 7*[PieceType.PAWN]
        self.time_left = time_left 

    def remove_piece(self, p_type: PieceType) -> None:
        self.piecesLeft.remove(p_type)

    def add_piece(self, p_type: PieceType) -> None:
        self.piecesLeft.append(p_type)

