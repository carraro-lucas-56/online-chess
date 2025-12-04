from piece import *

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

    @property
    def back_rank_layout(self):
        return self.__back_rank_layout

    def _initial_position(self):
        # Create an empty 8x8 board represented by a list of lists
        board = [[None for _ in range(8)] for _ in range(8)]
        
        # Place black pieces (row 0 and row 1)
        board[0] = [self._create_piece(PieceColor.BLACK, piece_type, 0, y) 
                    for y, piece_type in enumerate(self.back_rank_layout)]
        board[1] = [Pawn(PieceColor.BLACK, (1, y)) for y in range(8)]
        
        # Place white pieces (row 6 and row 7)
        board[6] = [Pawn(PieceColor.WHITE, (6, y)) for y in range(8)]
        board[7] = [self._create_piece(PieceColor.WHITE, piece_type, 7, y) 
                    for y, piece_type in enumerate(self.back_rank_layout)]
        
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
            raise ValueError(f"Invalid piece type: {piece_t}")

    
    def _apply_move(self, x: int, y: int, x2: int, y2: int) -> None:
        """
        Changes pieces positions in order to apply the move
        (x,y) -> current coordinate of the piece to be moved
        (x2,y2) -> destination coordinate for the piece being moved
        """

        orig = self.board[x][y] 
        dest = self.board[x2][y2]         

        self.board[x2][y2] = orig 
        self.board[x][y] = None


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

