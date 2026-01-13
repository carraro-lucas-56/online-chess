import numpy as np

from src.piece import (Piece, PieceState, PieceType, PieceColor,  
                       Move, MoveType, create_piece)


class ChessBoard():
    def __init__(self,customBoard: np.ndarray | None = None):
        self.__white_back_rank_layout = ['R','N','DB','Q','K','LB','N','R']
        self.__black_back_rank_layout = ['R','N','LB','Q','K','DB','N','R']
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
            board[0, y] = create_piece(PieceColor.BLACK, PieceType(piece_type), 0, y)
        board[1] = [create_piece(PieceColor.BLACK, PieceType.PAWN, 1, y) for y in range(8)]
        
        # Place white pieces (row 6 and row 7)
        board[6] = [create_piece(PieceColor.WHITE, PieceType.PAWN, 6, y) for y in range(8)]
        for y, piece_type in enumerate(self.white_back_rank_layout):
            board[7, y] = create_piece(PieceColor.WHITE, PieceType(piece_type), 7, y)
        
        return board

    def reset(self):
        """
        Set the board back to the initial position.
        """
        self.board = self._initial_position()

    def is_checked(self, turn: PieceColor) -> bool:
        """
        Return true if the king of the given color is checked
        """
        for piece in self.board.flat:
            # Empty square or friendly piece
            if not piece or piece.color == turn:
                continue
            
            # Check for moves that attack the king  
            if next((move for move in piece.get_moves(self.board) 
                        if self.board[move.coords[2]][move.coords[3]] and 
                           self.board[move.coords[2]][move.coords[3]].type == PieceType.KING),None):
                return True
        
        return False
    
    def gen_valid_moves(self, turn: PieceColor, lastMove: Move | None = None) -> list[Move]:
        """
        Generate a list with all the valid moves for a given color in the current chess position.
        """
        valid_moves, moves = [], []

        # First get all the spatially possible captures and normal moves
        for piece in self.board.flat:
            if piece and piece.color == turn:
                moves.extend(piece.get_moves(self.board))

        # Iterate over all the moves to check if they're valid.
        # First we apply the move in the board.
        # If the king is checked in the resulting board, the move isn't valid. 
        for move in moves:
            (x,y) = move.coords[0:2]
            old_state = self.board[x][y].state

            piece_captured = self.apply_move(move)
            
            if(not self.is_checked(turn)):
                valid_moves.append(move)

            self.undo_move(move,piece_captured,old_state)

        """
        checking for available en passant captures
        """

        # Coords of a pawn that can be captured in passant
        pawn_coords = None

        # Checking if the last move is a two square pawn advance
        if lastMove:        
            (r,c) = lastMove.coords[2:]
            piece_moved = self.board[r][c]
            if piece_moved.type == PieceType.PAWN and abs(piece_moved.initial_row-r) == 2:
                pawn_coords = (r,c)

        if pawn_coords:
            # aux tells which direction that pawn moves
            aux = 1 if turn == PieceColor.BLACK else -1

            # Checks the squares in the right/left from the target pawn
            for y in [c+1,c-1]:
                if(y > 7 or y < 0):
                    continue

                piece = self.board[r][y]

                # There's no pawn to perform the en passant capture
                if(not piece or piece.type != PieceType.PAWN):
                    continue

                enpassant_cap = Move((r,y,r+aux,c),MoveType.ENPASSANT)

                pawn_captured = self.apply_move(enpassant_cap)

                if not self.is_checked(turn):   
                    valid_moves.append(enpassant_cap)

                self.undo_move(enpassant_cap,pawn_captured)

        """
        Checking for available castling moves
        """

        # Back rank row
        row = 0 if turn == PieceColor.BLACK else 7

        # King needs to be is in the right spot and must have not moved yet
        if (not self.board[row][4] 
            or self.board[row][4].type != PieceType.KING 
            or self.board[row][4].state == PieceState.MOVED):
            return valid_moves 

        # Getting the coords from the squares in the desired row that are being attacked by the opponent 
        attacked_squares = []        
        for piece in self.board.flat:
            if not piece or piece.color == turn:
                continue
            elif piece.type == PieceType.PAWN:
                attacked_squares.extend(piece.attacked_squares())
            else:
                attacked_squares.extend([
                    move.coords[2:]
                    for move in piece.get_moves(self.board) 
                    if move.coords[2] == row])

        for (col,aux) in [(0,-1),(7,1)]:
            # Rook needs to be in the right sopt and must have not moved yet
            if (not self.board[row][col] 
                or self.board[row][col].type != PieceType.ROOK 
                or self.board[row][col].state == PieceState.MOVED):
                continue    
            
            # The path between the king and the rook must be empty
            if (self.board[row][4+aux] 
                or self.board[row][4+2*aux] 
                or (col == 0 and self.board[row][4+3*aux])): # The path is longer for long castling
                continue
            
            squares_to_check = [
            (row, 4),
            (row, 4 + aux),  
            (row, 4 + 2 * aux)
            ]

            # If the king or the squares it must walk are attacked we can't castle
            if any(square in attacked_squares for square in squares_to_check):
                continue

            valid_moves.append(Move((row,4,row,4+2*aux),MoveType.CASTLE))

        return valid_moves                

    def undo_move(self, move: Move, piece_captured: Piece | None = None, piece_old_state: PieceState | None = None) -> None:
        """
        Undo a given chess move.

        piece_old_state is the state of the piece who moved before the move was performed, that's important
        when we're undoing the first move the piece made in the match.
        """
        (x,y,x2,y2) = move.coords
        
        # Put the piece back on the origin square and updates its position
        if(move.type == MoveType.PROMOTION_CAPTURE or move.type == MoveType.PROMOTION_NORMAL):
            self.board[x][y] = create_piece(self.board[x2][y2].color,PieceType.PAWN,x,y)
        else:
            self.board[x][y] = self.board[x2][y2]
            self.board[x][y].position = (x,y)

        if(move.type == MoveType.ENPASSANT):
            # Putting the captured pawn back to the left or right square
            self.board[x][y2] = piece_captured

            self.board[x2][y2] = None
        else:
            self.board[x][y].state = piece_old_state

            # Putting the captured piece back in the board
            self.board[x2][y2] = piece_captured

        if(move.type == MoveType.CASTLE):
            # Rook col
            (aux,r_col) = (-1,7) if y-y2 < 0 else (1,0)
            
            self.board[x][r_col] = self.board[x][y2+aux]
            self.board[x][r_col].position = (x,r_col)
            self.board[x][y2+aux].state = PieceState.NOT_MOVED
            self.board[x][y2+aux] = None
            

    def apply_move(self, move: Move) -> None | Piece:
        """
        Changes piece positions in order to apply the move.
        
        Returns a Piece object if the move is a capture or None if it's a normal move.
        """
        (x,y,x2,y2) = move.coords
        piece = self.board[x][y]
        captured_piece = None

        # Emptying the square where the piece was
        self.board[x][y] = None

        match move.type:
            case MoveType.PROMOTION_NORMAL |  MoveType.PROMOTION_CAPTURE:
                piece = create_piece(piece.color,move.promotion,x2,y2)
                if move.type == MoveType.PROMOTION_CAPTURE:
                    captured_piece = self.board[x2][y2]    

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
                self.board[x][r_col2].state = PieceState.MOVED
        
        # Putting the moving piece in the destination square
        self.board[x2][y2] = piece 
        self.board[x2][y2].position = (x2,y2)
        self.board[x2][y2].state = PieceState.MOVED

        return captured_piece

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

