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

    def update_position(self, new_position: tuple[int,int]) -> None:
        self.position = new_position

    @classmethod
    def _in_bound(self, x: int, y: int) -> bool:
        """
        helper function to check if a coordinate in valid
        """
        return x >= 0 and y >= 0 and x <= 7 and y <= 7

    @abstractmethod
    def get_moves(self, board) -> list[tuple[int,int,int,int]]:
        """
        Return all spatially possible moves for the piece in the given board.
        Those moves ARE NOT necessarily valid.
        Move validations are done in a different section of the code.
        """

    def _explore_directions(self, board, dirs: list[tuple[int,int]]) -> list[tuple[int,int,int,int]]:
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
                moves.append((r,c,r+x,c+y))
                x += dr
                y += dc

            # stop, we found another piece 
            else:
                # if it's an opposing piece add the capture move
                if board[r+x][c+y].color != self.color:
                    moves.append((r,c,r+x,c+y)) 

                # change the diagonal we're exploring
                index += 1
                (dr,dc) = dirs[index%len(dirs)]
                x, y = dr, dc

        return moves

    @classmethod
    def _piece_value(piece: PieceType) -> int:
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

    def get_moves(self, board) -> list[tuple[int,int,int,int]]:
        moves = []

        # aux helps with board orientation
        aux = 1 if self.color == PieceColor.BLACK else -1

        (r,c) = self.position

        # checks the condtions to make a capture in the left up square
        if self._in_bound(r+aux,c-1) and board[r+aux][c-1] and board[r+aux][c-1].color != self.color:
            moves.append((r,c,r+aux,c-1))

        # checks the condtions to make a capture in the right up square
        if self._in_bound(r+aux,c+1) and board[r+aux][c+1] and board[r+aux][c+1].color != self.color:
            moves.append((r,c,r+aux,c+1))

        # checks if we can go one square up
        if self._in_bound(r+aux,c) and board[r+aux][c] is None:
            moves.append((r,c,r+aux,c))

            # checks if we can go two squares up
            if self._in_bound(r+2*aux,c) and self.state == PieceState.NOT_MOVED and board[r+2*aux][c] is None:
                moves.append((r,c,r+2*aux,c))

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
            # checks if the destination squal is empty or has an opposing piece
            if self._in_bound(x,y) and (board[x][y] is None or board[x][y].color != self.color):
                moves.append((r,c,x,y))

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
            if(self._in_bound(r+dr,c+dc) and (board[r+dr][c+dc] is None or board[r+dr][c+dc].color != self.color)):
                moves.append((r,c,r+dr,c+dc))

        return moves
    