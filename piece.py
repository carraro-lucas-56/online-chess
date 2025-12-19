from enum import Enum
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

class PieceColor(Enum):
    WHITE = 1
    BLACK = 2

class PieceState(Enum):
    MOVED = 1
    NOT_MOVED = 2

class MoveType(Enum):
    NORMAL = 1
    CAPTURE = 2
    ENPASSANT = 3
    CASTLE = 4
    PROMOTION_NORMAL = 5
    PROMOTION_CAPTURE = 6

class PieceType(Enum):
    QUEEN = "Q"
    ROOK = "R"
    BISHOP = "B"
    KNIGHT = "N"

@dataclass
class Move:
    coords: tuple[int,int,int,int]
    type: MoveType
    promotion: Optional[PieceType] = None

class Piece(ABC):
    def __init__(self,
                 color: PieceColor,
                 piece_type: str,
                 position: tuple[int,int]):
        self.__color = color
        self.__value = self._piece_value(piece_type)
        self.state = PieceState.NOT_MOVED
        self.position = position

    @property
    def color(self):
        return self.__color

    @property
    def value(self):
        return self.__value

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
                if board[r+x][c+y].color != self.color and type(board[r+x][c+y] != King):
                    moves.append(Move((r,c,r+x,c+y),MoveType.CAPTURE)) 

                # change the diagonal we're exploring
                index += 1
                (dr,dc) = dirs[index%len(dirs)]
                x, y = dr, dc

        return moves

    @classmethod
    def _piece_value(cls,piece_type: str) -> int:
        piece_value_dict = {
            "P" : 1,
            "N" : 3,
            "B" : 3,
            "R" : 5,
            "Q" : 10,
            "K" : 1000
        }
        return piece_value_dict[piece_type]
    
class Pawn(Piece):
    def __init__(self, color: PieceColor, position: tuple[int,int]):
        super().__init__(color,
                         "P",
                         position)
        self.inital_row = 6 if self.color == PieceColor.WHITE else 1

    def attacked_squares(self) -> list[tuple[int,int]]:
        """
        Returns the coordinates of all the coords that the pawn is attacking
        """
        aux = 1 if self.color == PieceColor.BLACK else -1
        (r,c) = self.position

        return [(x,y) for (x,y) in [(r+aux,c-1),(r+aux,c+1)] if self._in_bound(x,y)]

    def get_promotion_moves(self,board) -> list[Move]:
        """
        Generate promotions moves
        """
        moves = []
        (r,c) = self.position

        # aux helps with board orientation
        aux = 1 if self.color == PieceColor.BLACK else -1

        # Checks the condtions to promote with a capture in the left up square
        if (self._in_bound(r+aux,c-1) 
            and board[r+aux][c-1] 
            and board[r+aux][c-1].color != self.color):
            moves.extend([Move((r,c,r+aux,c-1,),MoveType.PROMOTION_CAPTURE,p_type) 
                          for p_type in PieceType])

        # Checks the condtions to promote with a capture in the right up square
        if (self._in_bound(r+aux,c+1) 
            and board[r+aux][c+1] 
            and board[r+aux][c+1].color != self.color):
            moves.extend([Move((r,c,r+aux,c+1,),MoveType.PROMOTION_CAPTURE,p_type) 
                          for p_type in PieceType])

        # Checks if we can go one square up
        if self._in_bound(r+aux,c) and board[r+aux][c] is None:
            moves.extend([Move((r,c,r+aux,c,),MoveType.PROMOTION_NORMAL,p_type) 
                          for p_type in PieceType])
            
        return moves

    def get_moves(self, board) -> list[Move]:
        (r,c) = self.position

        # Pawn is about to promote
        if(self.color == PieceColor.BLACK and r == 6) or (self.color == PieceColor.WHITE and r == 1):
            return self.get_promotion_moves(board)

        moves = []

        # aux helps with board orientation
        aux = 1 if self.color == PieceColor.BLACK else -1

        # Checks the condtions to make a capture in the left up square
        if (self._in_bound(r+aux,c-1) 
            and board[r+aux][c-1] 
            and board[r+aux][c-1].color != self.color):
            moves.append(Move((r,c,r+aux,c-1,),MoveType.CAPTURE))

        # Checks the condtions to make a capture in the right up square
        if (self._in_bound(r+aux,c+1) 
            and board[r+aux][c+1] 
            and board[r+aux][c+1].color != self.color):
            moves.append(Move((r,c,r+aux,c+1),MoveType.CAPTURE))

        # Checks if we can go one square up
        if board[r+aux][c] is None:
            moves.append(Move((r,c,r+aux,c),MoveType.NORMAL))

            # Checks if we can go two squares up
            if r == self.inital_row and board[r+2*aux][c] is None:
                moves.append(Move((r,c,r+2*aux,c),MoveType.NORMAL))

        return moves    
        
class Knight(Piece):
    def __init__(self, color: PieceColor, position: tuple[int,int]):
        super().__init__(color,
                         "N",
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
                         "B",
                         position)

    def get_moves(self, board):
        diagonals = [(1,1),(1,-1),(-1,1),(-1,-1)]
        return self._explore_directions(board,diagonals)

class Rook(Piece):
    def __init__(self, color: PieceColor, position: tuple[int,int]):
        super().__init__(color,
                         "R",
                         position)

    def get_moves(self, board):
        # vertical and horizontal directions
        dirs = [(0,1),(0,-1),(1,0),(-1,0)]
        return self._explore_directions(board,dirs)

class Queen(Piece):
    def __init__(self, color: PieceColor, position: tuple[int,int]):
        super().__init__(color,
                         "Q",
                         position)

    def get_moves(self, board):
        all_dirs = [(1,1),(1,-1),(-1,1),(-1,-1),(0,1),(0,-1),(1,0),(-1,0)]
        return self._explore_directions(board,all_dirs) 
        
class King(Piece):
    def __init__(self, color: PieceColor, position: tuple[int,int]):
        super().__init__(color,
                         "K",
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
    