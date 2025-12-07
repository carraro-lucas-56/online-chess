from piece import *
import numpy as np

class MoveType(Enum):
    REGULAR = 1
    CAPTURE = 2
    CASTLE = 3
    ENPASSANT = 4

class ChessBoard():
    def __init__(self):
        self.__back_rank_layout = [PieceType.ROOK, 
                                   PieceType.KNIGHT,
                                   PieceType.BISHOP,
                                   PieceType.QUEEN,
                                   PieceType.KING,
                                   PieceType.BISHOP,
                                   PieceType.KNIGHT,
                                   PieceType.ROOK]
        self.board = self._initial_position()  
        self.blackKing = (0,4)
        self.whiteKing = (7,4)

    @property
    def back_rank_layout(self):
        return self.__back_rank_layout

    def _initial_position(self):
        # Create an empty 8x8 board using numpy
        board = np.full((8, 8), None, dtype=object)  # Initially set all positions to None
        
        # Place black pieces (row 0 and row 1)
        for y, piece_type in enumerate(self.back_rank_layout):
            board[0, y] = self._create_piece(PieceColor.BLACK, piece_type, 0, y)
        board[1] = [Pawn(PieceColor.BLACK, (1, y)) for y in range(8)]
        
        # Place white pieces (row 6 and row 7)
        board[6] = [Pawn(PieceColor.WHITE, (6, y)) for y in range(8)]
        for y, piece_type in enumerate(self.back_rank_layout):
            board[7, y] = self._create_piece(PieceColor.WHITE, piece_type, 7, y)
        
        return board


    def _create_piece(self, color: PieceColor, piece_type: PieceType, row: int, col: int):
        """
        Helper function to create the correct piece based on type.
        """
        if piece_type == PieceType.PAWN:
            return Pawn(color, (row, col))
        elif piece_type == PieceType.KNIGHT:
            return Knight(color, (row, col))
        elif piece_type == PieceType.BISHOP:
            return Bishop(color, (row, col))
        elif piece_type == PieceType.ROOK:
            return Rook(color, (row, col))
        elif piece_type == PieceType.QUEEN:
            return Queen(color, (row, col))
        elif piece_type == PieceType.KING:
            return King(color, (row, col))
        else:
            raise ValueError(f"Invalid piece type: {piece_type}")

    def _is_checked(self, turn: PieceColor) -> bool:
        """
        Return true if the king of the given color is checked
        """
        kingPosition = self.whiteKing if turn == PieceColor.WHITE else self.blackKing
        attacked_pieces = [] # coords of all the pieces being attacked by the opponent


        for piece in self.board.flat:
            if piece and piece.color != turn:
                # get only the moves that have a piece in the destination coordinate
                attacked_pieces.extend([(x,y) for (_,_,x,y) in piece.get_moves(self.board) if self.board[x][y]])

        return kingPosition in attacked_pieces
    
    def gen_valid_moves(self, turn: PieceColor) -> list[tuple[int,int,int,int]]:
        """
        Generate a list with all the valid moves for a given color in the current chess position
        """
        valid_moves = []
        moves = []

        # first get all the spatially passible moves
        for piece in self.board.flat:
            if piece and piece.color == turn:
                moves.extend(piece.get_moves(self.board))

        """
        Iterate over all the moves to check if they're valid.
        First we apply the move in the board.
        If the king is checked in the resulting board, the move isn't valid. 
        """
        for move in moves:
            piece_captured = self._apply_move(move)
            
            if(not self._is_checked(turn)):
                valid_moves.append(move)

            (x,y,x2,y2) = move

            # undo the changes made on the board in _apply_move so we can repeat the process
            self.board[x][y] = self.board[x2,y2]
            self.board[x][y].update_position((x,y))

            if(self.board[x][y].type == PieceType.KING):
                if(turn == PieceColor.BLACK):
                    self.blackKing = (x,y)
                else:
                    self.whiteKing = (x,y)

            self.board[x2][y2] = piece_captured 

        return valid_moves                

    def _apply_move(self, move: tuple[int,int,int,int]) -> None | Piece:
        """
        Changes piece positions in order to apply the move
        """
        (x,y,x2,y2) = move

        # code to performe a regular move or a capture move
        piece = self.board[x][y]
        piece.update_position((x2,y2))
        
        captured_piece = self.board[x2][y2] 

        # putting the piece in the destination square
        self.board[x2][y2] = piece 

        # emptying the square the piece was
        self.board[x][y] = None

        # code to performe enPassant capture
        # ...

        # code to performe castle move
        # ...

        # updates king position if necessary
        if piece.type == PieceType.KING:
            if(piece.color == PieceColor.BLACK):
                self.blackKing = (x2,y2)
            else:
                self.whiteKing = (x2,y2)

        self.board[x2][y2].state = PieceState.MOVED

        return captured_piece

    def print_board(self):
        """
        Prints the chessboard to the terminal using simple ASCII characters.
        Uppercase = White, lowercase = Black.
        """
        # Mapping piece types to letters
        piece_symbols = {
            PieceType.KING:   "K",
            PieceType.QUEEN:  "Q",
            PieceType.ROOK:   "R",
            PieceType.BISHOP: "B",
            PieceType.KNIGHT: "N",
            PieceType.PAWN:   "P"
        }

        print("    a   b   c   d   e   f   g   h")
        print("  +---+---+---+---+---+---+---+---+")

        for row in range(8):
            rank = 8 - row
            row_str = f"{rank} |"

            for col in range(8):
                piece = self.board[row][col]
                if piece is None:
                    row_str += "   |"
                else:
                    symbol = piece_symbols[piece.type]
                    # White uppercase, black lowercase
                    if piece.color == PieceColor.WHITE:
                        row_str += f" {symbol} |"
                    else:
                        row_str += f" {symbol.lower()} |"

            print(row_str + f" {rank}")
            print("  +---+---+---+---+---+---+---+---+")

        print("    a   b   c   d   e   f   g   h")

