from enum import Enum
from abc import ABC, abstractmethod
from dataclasses import dataclass

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

class MoveType(Enum):
    NORMAL = 1
    CAPTURE = 2
    ENPASSANT = 3
    CASTLE = 4

@dataclass
class Move:
    coords: tuple[int,int,int,int]
    type: MoveType

class Piece(ABC):
    def __init__(self,
                 color: PieceColor,
                 type: PieceType,
                 position: tuple[int,int]):
        self.__color = color
        self.__type = type
        self.__value = self._piece_value(type)
        self.state = PieceState.NOT_MOVED
        self.position = position

    @property
    def color(self):
        return self.__color

    @property
    def value(self):
        return self.__value

    @property
    def type(self):
        return self.__type

    def update_position(self, new_position: tuple[int,int]) -> None:
        self.position = new_position

    @staticmethod
    def _in_bound(x: int, y: int) -> bool:
        """
        helper function to check if a coordinate in valid
        """
        return x >= 0 and y >= 0 and x <= 7 and y <= 7

    @abstractmethod
    def get_moves(self, board) -> list[Move]:
        """
        Return all spatially possible moves for the piece in the given board.
        Do not include en passant captures and castling.
        Those moves ARE NOT necessarily valid.
        Move validations are done in a different section of the code.
        """

    def _explore_directions(self, board, dirs: list[tuple[int,int]]) -> list[Move]:
        """
        This function 'walks' in the board with the piece in the given directions 
        and returns all the available moves it found.
        It is really usefull because it generalizes the code for moving Queen, Rook and Bishop
        We use tuple of 1's and 0's to represent the directions.
        Examples: (0,1) represents straight right direction, 
                  (-1,-1) represents the down left direction
        """
        
        moves = []        
        (r,c) = self.position
        
        # index counts the number of directions we already explored
        index = 0

        (dr,dc) = dirs[index]
        (x,y) = (dr,dc)
        
        # explore each diagonal one by one
        while(index < len(dirs)):

            # checking if we reached the end of the board
            if(not self._in_bound(r+x,c+y)):
                # if true change the diagonal
                index += 1
                (dr,dc) = dirs[index%len(dirs)]
                x, y = dr, dc

            # if the square is empty, keep exploring this diagonal
            elif(board[r+x][c+y] is None):
                moves.append(Move((r,c,r+x,c+y),MoveType.NORMAL))
                x += dr
                y += dc

            # stop, we found another piece 
            else:
                # if it's an opposing piece add the capture move
                if board[r+x][c+y].color != self.color:
                    moves.append(Move((r,c,r+x,c+y),MoveType.CAPTURE)) 

                # change the diagonal we're exploring
                index += 1
                (dr,dc) = dirs[index%len(dirs)]
                x, y = dr, dc

        return moves

    @classmethod
    def _piece_value(cls,piece: PieceType) -> int:
        piece_value_dict = {
            "PAWN" : 1,
            "KNIGHT" : 3,
            "BISHOP" : 3,
            "ROOK" : 5,
            "QUEEN" : 10,
            "KING" : 1000
        }
        return piece_value_dict[piece.name]
    
class Pawn(Piece):
    def __init__(self, color: PieceColor, position: tuple[int,int]):
        super().__init__(color,
                         PieceType.PAWN,
                         position)

    def get_moves(self, board) -> list[Move]:
        moves = []

        # aux helps with board orientation
        aux = 1 if self.color == PieceColor.BLACK else -1

        (r,c) = self.position

        # checks the condtions to make a capture in the left up square
        if self._in_bound(r+aux,c-1) and board[r+aux][c-1] and board[r+aux][c-1].color != self.color:
            moves.append(Move((r,c,r+aux,c-1,),MoveType.CAPTURE))

        # checks the condtions to make a capture in the right up square
        if self._in_bound(r+aux,c+1) and board[r+aux][c+1] and board[r+aux][c+1].color != self.color:
            moves.append(Move((r,c,r+aux,c+1),MoveType.CAPTURE))

        # checks if we can go one square up
        if self._in_bound(r+aux,c) and board[r+aux][c] is None:
            moves.append(Move((r,c,r+aux,c),MoveType.NORMAL))

            # checks if we can go two squares up
            if self._in_bound(r+2*aux,c) and self.state == PieceState.NOT_MOVED and board[r+2*aux][c] is None:
                moves.append(Move((r,c,r+2*aux,c),MoveType.NORMAL))

        return moves    
        
class Knight(Piece):
    def __init__(self, color: PieceColor, position: tuple[int,int]):
        super().__init__(color,
                         PieceType.KNIGHT,
                         position)

    def get_moves(self, board):
        moves = []
        (r,c) = self.position

        # all possible destination coords for paths in 'L'
        coords = [
        (r+2, c+1), (r+2, c-1),
        (r-2, c+1), (r-2, c-1),
        (r+1, c+2), (r+1, c-2),
        (r-1, c+2), (r-1, c-2)
        ]
        
        for (x,y) in coords:
            if not self._in_bound(x,y):
                continue 

            # checks if the destination square is empty or has an opposing piece
            if(board[x][y] is None):
                moves.append(Move((r,c,x,y),MoveType.NORMAL))
            elif( board[x][y].color != self.color):
                moves.append(Move((r,c,x,y),MoveType.CAPTURE))

        return moves

class Bishop(Piece):
    def __init__(self, color: PieceColor, position: tuple[int,int]):
        super().__init__(color,
                         PieceType.BISHOP,
                         position)

    def get_moves(self, board):
        diagonals = [(1,1),(1,-1),(-1,1),(-1,-1)]
        return self._explore_directions(board,diagonals)

class Rook(Piece):
    def __init__(self, color: PieceColor, position: tuple[int,int]):
        super().__init__(color,
                         PieceType.ROOK,
                         position)

    def get_moves(self, board):
        # vertical and horizontal directions
        dirs = [(0,1),(0,-1),(1,0),(-1,0)]
        return self._explore_directions(board,dirs)

class Queen(Piece):
    def __init__(self, color: PieceColor, position: tuple[int,int]):
        super().__init__(color,
                         PieceType.QUEEN,
                         position)

    def get_moves(self, board):
        all_dirs = [(1,1),(1,-1),(-1,1),(-1,-1),(0,1),(0,-1),(1,0),(-1,0)]
        return self._explore_directions(board,all_dirs) 
        
class King(Piece):
    def __init__(self, color: PieceColor, position: tuple[int,int]):
        super().__init__(color,
                         PieceType.KING,
                         position)
        
    def get_moves(self, board):
        moves = []
        all_dirs = [(1,1),(1,-1),(-1,1),(-1,-1),(0,1),(-1,0),(0,-1),(1,0)]
        (r,c) = self.position

        for (dr,dc) in all_dirs:
            if(not self._in_bound(r+dr,c+dc)):
                continue 
        
            # checks if the destination square is empty or has an opposing piece
            if board[r+dr][c+dc] is None:
                moves.append(Move((r,c,r+dr,c+dc),MoveType.NORMAL))
            elif( board[r+dr][c+dc].color != self.color):
                moves.append(Move((r,c,r+dr,c+dc),MoveType.CAPTURE))

        return moves
    