from piece import *
import numpy as np

class ChessBoard():
    def __init__(self,customBoard: np.ndarray | None = None):
        self.__back_rank_layout = ['R','N','B','Q','K','B','N','R']
        self.board = customBoard if not customBoard is None else self._initial_position()  

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

    def _create_piece(self, color: PieceColor, piece_type: str, row: int, col: int) -> Piece:
        """
        Helper function to create the correct piece based on type.
        """

        if piece_type == 'N':
            return Knight(color, (row, col))
        elif piece_type == 'B':
            return Bishop(color, (row, col))
        elif piece_type == 'R':
            return Rook(color, (row, col))
        elif piece_type == 'Q':
            return Queen(color, (row, col))
        elif piece_type == 'K':
            return King(color, (row, col))
        elif piece_type == 'P':
            return Pawn(color, (row, col))
        else:
            raise ValueError(f"Invalid piece type: {piece_type}")

    def _is_checked(self, turn: PieceColor) -> bool:
        """
        Return true if the king of the given color is checked
        """
        for piece in self.board.flat:
            # Empty square or friendly piece
            if not piece or piece.color == turn:
                continue
            
            # Check for moves that attack the king  
            if [move for move in piece.get_moves(self.board) 
                if self.board[move.coords[2]][move.coords[3]] and type(self.board[move.coords[2]][move.coords[3]]) == King]:
                return True
        
        return False
    
    def gen_valid_moves(self, turn: PieceColor, lastMove: Move | None = None) -> list[Move]:
        """
        Generate a list with all the valid moves for a given color in the current chess position
        """
        valid_moves = []
        moves = []

        # first get all the spatially possible captures and normal moves
        for piece in self.board.flat:
            if piece and piece.color == turn:
                moves.extend(piece.get_moves(self.board))

        """
        Iterate over all the moves to check if they're valid.
        First we apply the move in the board.
        If the king is checked in the resulting board, the move isn't valid. 
        """
        for move in moves:
            (x,y) = move.coords[0:2]
            old_state = self.board[x][y].state

            # temporarily appying the move so we can check if it's valid
            piece_captured = self._apply_move(move)
            
            if(not self._is_checked(turn)):
                valid_moves.append(move)

            # undo the move so we can repeat the process
            self._undo_move(move,piece_captured,old_state)

        """
        checking for available en passant captures
        """

        # Row where a pawn must be to perform en passant capture
        # Aux tells which direction that pawn moves
        row, aux = (4, 1) if turn == PieceColor.BLACK else (3, -1)

        for piece in self.board[row]:
            # Only consider pawns
            if not piece or type(piece) != Pawn:
                continue

            r, c = piece.position

            # Two possible en passant capture destinations (left and right)
            targets = [
                (r + 2 * aux, c - 1, r, c - 1),
                (r + 2 * aux, c + 1, r, c + 1),
            ]

            for t_r2, t_c2, t_r1, t_c1 in targets:
                # Must match last move's coordinates
                if lastMove.coords != (t_r2, t_c2, t_r1, t_c1):
                    continue

                target_piece = self.board[r][t_c1]

                # Must be an enemy pawn in the adjacent file
                if not target_piece or type(target_piece) != Pawn:
                    continue

                # Construct the en passant capture move
                cap_move = Move((r, c, r + aux, t_c1), MoveType.ENPASSANT)

                # Temporarily apply the move to check legality
                pawn_captured = self._apply_move(cap_move)

                if not self._is_checked(turn):
                    valid_moves.append(cap_move)

                # Undo the temporary move
                self._undo_move(cap_move, pawn_captured)


        """
        Checking for available castling moves
        """

        # Back rank row
        row = 0 if turn == PieceColor.BLACK else 7

        # King needs to be is in the right spot and must have not moved yet
        if (not self.board[row][4] 
            or type(self.board[row][4]) != King 
            or self.board[row][4].state == PieceState.MOVED):
            return valid_moves 

        # Getting the coords from the squares in the desired row that are being attacked by the opponent 
        attacked_squares = []        
        for piece in self.board.flat:
            if not piece or piece.color == turn:
                continue
            elif type(piece) == Pawn:
                attacked_squares.extend(piece.attacked_squares())
            else:
                attacked_squares.extend([
                    (move.coords[2],move.coords[3]) 
                    for move in piece.get_moves(self.board) 
                    if move.coords[2] == row])

        for (col,aux) in [(0,-1),(7,1)]:
            # Rook needs to be in the right sopt and must have not moved yet
            if (not self.board[row][col] 
                or type(self.board[row][col]) != Rook 
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

    def _undo_move(self, move: Move, piece_captured: Piece | None = None, piece_old_state: PieceState | None = None) -> None:
        """
        Undo a given chess move.
        piece_old_state is the state of the piece who moved before the move was performed, that's important
        when we're undoing the first move the piece made in the match.
        """
        (x,y,x2,y2) = move.coords
        
        # Put the piece back on the origin square and updates its position
        if(move.type == MoveType.PROMOTION_CAPTURE or move.type == MoveType.PROMOTION_NORMAL):
            self.board[x][y] = self._create_piece(self.board[x2][y2].color,"P",x,y)
        else:
            self.board[x][y] = self.board[x2][y2]
            self.board[x][y].position = (x,y)

        if(move.type == MoveType.ENPASSANT):
            # Putting the captured pawn back to the left or right square
            self.board[x][y2] = piece_captured

            # Emptying the destination square
            self.board[x2][y2] = None
        else:
            self.board[x][y].state = piece_old_state

            # Putting the captured piece back in the board
            self.board[x2][y2] = piece_captured

    def _apply_move(self, move: Move) -> None | Piece:
        """
        Changes piece positions in order to apply the move.
        Returns a Piece object if the move is a capture or None if it's a normal move.
        """
        (x,y,x2,y2) = move.coords
        captured_piece = None
        piece = self.board[x][y]

        # Promoting the pawn into another piece
        if move.type == MoveType.PROMOTION_NORMAL or move.type == MoveType.PROMOTION_CAPTURE:
            piece = self._create_piece(piece.color,move.promotion.value,x2,y2)

        # Emptying the square where the piece was
        self.board[x][y] = None

        if(move.type == MoveType.CAPTURE or move.type == MoveType.PROMOTION_CAPTURE):
            captured_piece = self.board[x2][y2] 

        elif(move.type == MoveType.ENPASSANT):
            # In a enpassant capture the captured piece is on the left or right side of the moving piece
            captured_piece = self.board[x][y2]
            self.board[x][y2] = None

        elif(move.type == MoveType.CASTLE):
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
        # Mapping piece types to letters
        piece_symbols = {
            King:   "K",
            Queen:  "Q",
            Rook:   "R",
            Bishop: "B",
            Knight: "N",
            Pawn:   "P"
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
                    symbol = piece_symbols[type(piece)]
                    # White uppercase, black lowercase
                    if piece.color == PieceColor.WHITE:
                        row_str += f" {symbol} |"
                    else:
                        row_str += f" {symbol.lower()} |"

            print(row_str + f" {rank}")
            print("  +---+---+---+---+---+---+---+---+")

        print("    a   b   c   d   e   f   g   h")

