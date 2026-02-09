import numpy as np

from .piece import (Piece, PieceType, PieceColor,  
                       Move, MoveType, create_piece)

class ChessBoard():
    def __init__(self,customBoard: np.ndarray | None = None):
        self.__white_back_rank_layout = [PieceType.ROOK,PieceType.KNIGHT,PieceType.DARK_BISHOP,PieceType.QUEEN,PieceType.KING,PieceType.LIGHT_BISHOP,PieceType.KNIGHT,PieceType.ROOK]
        self.__black_back_rank_layout = [PieceType.ROOK,PieceType.KNIGHT,PieceType.LIGHT_BISHOP,PieceType.QUEEN,PieceType.KING,PieceType.DARK_BISHOP,PieceType.KNIGHT,PieceType.ROOK]
        self.board = customBoard if not customBoard is None else self._initial_position()  

    @property
    def white_back_rank_layout(self):
        return self.__white_back_rank_layout

    @property
    def black_back_rank_layout(self):
        return self.__black_back_rank_layout

    def _initial_position(self):
        # Create an empty 8x8 board using numpy
        board = np.full((8, 8), None, dtype=object)  # Initially set all positions to None
        
        # Place black pieces (row 0 and row 1)
        for y, piece_type in enumerate(self.black_back_rank_layout):
            board[0, y] = create_piece(PieceColor.BLACK, piece_type, 0, y)
        board[1] = [create_piece(PieceColor.BLACK, PieceType.PAWN, 1, y) for y in range(8)]
        
        # Place white pieces (row 6 and row 7)
        board[6] = [create_piece(PieceColor.WHITE, PieceType.PAWN, 6, y) for y in range(8)]
        for y, piece_type in enumerate(self.white_back_rank_layout):
            board[7, y] = create_piece(PieceColor.WHITE, piece_type, 7, y)
        
        return board

    def reset(self):
        """
        Set the board back to the initial position.
        """
        self.board = self._initial_position()

    def is_checked(self, turn: PieceColor, pieces: list[Piece]) -> bool:
        """
        Return True if the king of `turn` is in check.
        """

        # 1) Find king square
        king = next(p for p in pieces if p.type == PieceType.KING)
        kr, kc = king.position

        enemy = PieceColor.BLACK if turn == PieceColor.WHITE else PieceColor.WHITE
        board = self.board

        # 2) Pawn attacks
        pawn_dir = 1 if enemy == PieceColor.WHITE else -1
        for dc in (-1, 1):
            r, c = kr + pawn_dir, kc + dc
            if 0 <= r < 8 and 0 <= c < 8:
                p = board[r][c]
                if p and p.color == enemy and p.type == PieceType.PAWN:
                    return True

        # 3) Knight attacks
        knight_offsets = [
            (-2, -1), (-2, 1), (-1, -2), (-1, 2),
            (1, -2),  (1, 2),  (2, -1),  (2, 1)
        ]
        for dr, dc in knight_offsets:
            r, c = kr + dr, kc + dc
            if 0 <= r < 8 and 0 <= c < 8:
                p = board[r][c]
                if p and p.color == enemy and p.type == PieceType.KNIGHT:
                    return True

        # 4) Sliding pieces (rook / bishop / queen)
        directions = [
            (-1, 0), (1, 0), (0, -1), (0, 1),      # rook directions
            (-1, -1), (-1, 1), (1, -1), (1, 1)     # bishop directions
        ]

        for dr, dc in directions:
            r, c = kr + dr, kc + dc
            while 0 <= r < 8 and 0 <= c < 8:
                p = board[r][c]
                if p:
                    if p.color == enemy:
                        if (
                            (dr == 0 or dc == 0) and p.type in (PieceType.ROOK, PieceType.QUEEN)
                            or
                            (dr != 0 and dc != 0) and p.type in (PieceType.DARK_BISHOP, PieceType.LIGHT_BISHOP, PieceType.QUEEN)
                        ):
                            return True
                    break
                r += dr
                c += dc

        # 5) Enemy king (adjacent squares)
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                r, c = kr + dr, kc + dc
                if 0 <= r < 8 and 0 <= c < 8:
                    p = board[r][c]
                    if p and p.color == enemy and p.type == PieceType.KING:
                        return True

        return False
    
    def get_attacked_squares(self, color: PieceColor) -> list[tuple[int,int]]:
        """ 
        Return which coords in the back rank are being attacked by the given color.
        """
        
        # back rank row
        row = 7 if color == PieceColor.BLACK else 0

        attacked_squares = []
        for piece in self.board.flat:
            if not piece or piece.color != color:
                continue
            elif piece.type == PieceType.PAWN:
                attacked_squares.extend(piece.attacked_squares())
            else:
                attacked_squares.extend([
                    move.coords[2:]
                    for move in piece.get_moves(self.board) 
                    if move.coords[2] == row])

        return attacked_squares

    def gen_valid_moves(self, turn: PieceColor, pieces: list[Piece], oppsPieces: list[Piece], CK: bool, CQ: bool, enpassant_square: tuple[int,int] | None = None) -> list[Move]:
        """
        Generate a list with all the valid moves for a given color in the current chess position.
        """
        valid_moves, moves = [], []

        # First get all the spatially possible captures and normal moves
        for piece in pieces:
            moves.extend(piece.get_moves(self.board))

        # Iterate over all the moves to check if they're valid.
        # First we apply the move in the board.
        # If the king is checked in the resulting board, the move isn't valid. 
        for move in moves:
            pawn_promoted, piece_captured = self.apply_move(move)
            
            if(not self.is_checked(turn,pieces)):
                valid_moves.append(move)

            self.undo_move(move,pawn_promoted,piece_captured)

        """
        checking for available en passant captures
        """

        if enpassant_square:                                                                                                                                                                                                                                                                                     
            # aux tells which direction that pawn moves                                                                                                                                                                                                                                                                                                                                                                                                                                     
            aux = 1 if turn == PieceColor.BLACK else -1
            (r,c) = enpassant_square

            # Checks the squares in the right/left from the target pawn
            for y in [c+1,c-1]:
                if(y > 7 or y < 0):
                    continue                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            

                piece = self.board[r][y]

                # There's no pawn to perform the en passant capture
                if(not piece or piece.type != PieceType.PAWN or piece.color != turn):
                    continue

                enpassant_cap = Move((r,y,r+aux,c),MoveType.ENPASSANT)

                _ ,pawn_captured = self.apply_move(enpassant_cap)

                if not self.is_checked(turn,pieces):   
                    valid_moves.append(enpassant_cap)

                self.undo_move(enpassant_cap,piece_captured=pawn_captured)

        """
        Checking for legal castling moves
        """

        # Back rank row
        row = 0 if turn == PieceColor.BLACK else 7
        attacked_squares = []

        if(not CK and not CQ):
            return valid_moves

        # Checking if kingside castle is legal
        if CK and not (self.board[row][5] or self.board[row][6]):
            
            attacked_squares = self.get_attacked_squares(PieceColor.BLACK if turn == PieceColor.WHITE else PieceColor.WHITE)
            
            if not any(square in attacked_squares for square in [(row,4),(row,5),(row,6)]):
                valid_moves.append(Move((row,4,row,6),MoveType.CASTLE))

        # Checking if queenside castle is legal
        if CQ and not (self.board[row][3] or self.board[row][2] or self.board[row][1]):
            
            if not attacked_squares:
                attacked_squares = self.get_attacked_squares(PieceColor.BLACK if turn == PieceColor.WHITE else PieceColor.WHITE)

            if any(square in attacked_squares for square in [(row,4),(row,3),(row,2)]):
                return valid_moves
            
            valid_moves.append(Move((row,4,row,2),MoveType.CASTLE))

        return valid_moves                

    def undo_move(self, move: Move, pawn_promoted: Piece | None = None ,piece_captured: Piece | None = None) -> None:
        """
        Undo a given chess move.
        """
        (x,y,x2,y2) = move.coords
        
        # Put the piece back on the origin square and updates its position
        if(move.type == MoveType.PROMOTION_CAPTURE or move.type == MoveType.PROMOTION_NORMAL):
            self.board[x][y] = pawn_promoted
        else:
            self.board[x][y] = self.board[x2][y2]
            self.board[x][y].position = (x,y)

        if(move.type == MoveType.ENPASSANT):
            # Putting the captured pawn back to the left or right square
            self.board[x][y2] = piece_captured

            self.board[x2][y2] = None
        else:
            # Putting the captured piece back in the board
            self.board[x2][y2] = piece_captured

        if(move.type == MoveType.CASTLE):
            # Rook col
            (sign,r_col) = (-1,7) if y-y2 < 0 else (1,0)
            
            self.board[x][r_col] = self.board[x][y2+sign]
            self.board[x][r_col].position = (x,r_col)
            self.board[x][y2+sign] = None
            
    def apply_move(self, move: Move) -> tuple[Piece | None, Piece | None]:
        """
        Changes piece positions in order to apply the move.
        
        Returns a Piece object if the move is a capture or None if it's a normal move.
        """
        (x,y,x2,y2) = move.coords
        piece = self.board[x][y]
        captured_piece = None
        pawn_promoted = None

        # Emptying the square where the piece was
        self.board[x][y] = None

        match move.type:
            case MoveType.PROMOTION_NORMAL |  MoveType.PROMOTION_CAPTURE:
                pawn_promoted = piece
                if move.type == MoveType.PROMOTION_CAPTURE:
                    captured_piece = self.board[x2][y2]    
                self.board[x2][y2] = create_piece(piece.color,move.promotion,x2,y2)

            case MoveType.CAPTURE:
                captured_piece = self.board[x2][y2] 

            case MoveType.ENPASSANT:
                # In a enpassant capture the captured piece is on the left or right side of the moving piece
                captured_piece = self.board[x][y2]
                self.board[x][y2] = None

            case MoveType.CASTLE:
                # Detecting if it's either short or long castle
                # r_col and r_col2 are the current rook's column and its destination column respectively
                (r_col,r_col2) = (7,5) if y2 == 6 else (0,3)

                # Moving the rook            
                self.board[x][r_col2] = self.board[x][r_col]
                self.board[x][r_col] = None
                self.board[x][r_col2].position = (x,r_col2)
        
        if move.type != MoveType.PROMOTION_CAPTURE and move.type != MoveType.PROMOTION_NORMAL: 
            # Putting the moving piece in the destination square
            self.board[x2][y2] = piece 
            self.board[x2][y2].position = (x2,y2)

        return pawn_promoted, captured_piece

    def print_board(self):
        """
        Prints the chessboard to the terminal using simple ASCII characters.

        Uppercase = White, lowercase = Black.
        """

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
                    symbol = (piece.type.value if piece.type != PieceType.LIGHT_BISHOP and piece.type != PieceType.DARK_BISHOP 
                                               else "B")
                    # White uppercase, black lowercase
                    if piece.color == PieceColor.WHITE:
                        row_str += f" {symbol} |"
                    else:
                        row_str += f" {symbol.lower()} |"

            print(row_str + f" {rank}")
            print("  +---+---+---+---+---+---+---+---+")

        print("    a   b   c   d   e   f   g   h")

