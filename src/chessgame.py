from src.chessboard import *
from src.piece import *
from src.player import *

class GameState(Enum):
    IN_PROGRESS = 1
    CHACKMATE = 2
    STALEMATE = 3
    DRAW_BY_75_MOVE_RULE = 4
    INSUFFICIENT_MATERIAL = 5
    NOT_STARTED = 6

class ChessGame():
    def __init__(self):
        self.turn = PieceColor.WHITE
        self.board = ChessBoard()
        self.state = GameState.NOT_STARTED
        self.white = Player(PieceColor.WHITE)
        self.black = Player(PieceColor.BLACK)
        self.validMoves = [] # List with all the valid moves current available for the colos who's playing in this turn 
        self.deadMoves = 0   

    def _change_turn(self) -> None:
        self.turn = PieceColor.WHITE if self.turn == PieceColor.BLACK else PieceColor.BLACK

    def _insufficient_material(self) -> bool:
        """
        Return True if no checkmate is possible at all, even with cooperation.
        """

        set_W = set(self.white.piecesLeft)
        set_B = set(self.black.piecesLeft)

        # Insufficient material combination
        k   = {PieceType.KING}
        kdb = {PieceType.KING,PieceType.DARK_BISHOP}
        klb = {PieceType.KING,PieceType.LIGHT_BISHOP}
        kn  = {PieceType.KING,PieceType.KNIGHT}

        ls = [k,kdb,klb,kn]

        if(len(set_W) >= 3 or 
           len(set_B) >= 3 or 
           set_W not in ls or 
           set_B not in ls):
            return False

        # King vs King
        if(set_W == k and set_B == k):
            return True
        # King + Bishop vs King + Bishop, any number of same-colored bishops
        elif((set_W == kdb and set_B == kdb) or (set_W == klb and set_B == klb)):
            return True
        # King + any number of same color bishops vs King
        elif (set_W == k and (set_B == kdb or set_B == klb)):
            return True
        # King + Knight vs lone King
        elif (set_W == k and set_B == kn and len(self.black.piecesLeft) == 2):
            return True
        # King + Knight vs King + Knight
        elif (set_W == kn and set_B == kn and len(self.white.piecesLeft) == 2 
                                          and len(self.black.piecesLeft) == 2 ):
            return True
        # King + Bishop vs King + Knight
        elif ((set_W == kdb or set_W == klb) and set_B == kn and len(self.white.piecesLeft) == 2 
                                                             and len(self.black.piecesLeft) == 2):
            return True


        # King + any number of same color bishops vs King
        elif (set_B == k and (set_W == kdb or set_W == klb)):
            return True
        # King + Knight vs lone King
        elif (set_B == k and set_W == kn and len(self.white.piecesLeft) == 2):
            return True
        # King + Bishop vs King + Knight
        elif ((set_B == kdb or set_B == klb) and set_W == kn and len(self.white.piecesLeft) == 2 
                                                             and len(self.black.piecesLeft) == 2):
            return True

        return False

    def _update_state(self) -> None:
        if not self.validMoves:
            self.state = (GameState.CHACKMATE 
                          if self.board.is_checked(self.turn)
                          else GameState.STALEMATE)
        elif self.deadMoves == 75:
            self.state = GameState.DRAW_BY_75_MOVE_RULE
        elif self._insufficient_material():
            self.state = GameState.INSUFFICIENT_MATERIAL

    def _update_player_data(self, p1: Player, p2: Player, move: Move) -> None:
        """
        Updates players's data based on the provided move.
        p1 is the player who made the move.
        """
        piece_captured = self.board.board[move.coords[2]][move.coords[3]] # Might be None depending on the move type

        if move.type == MoveType.PROMOTION_CAPTURE or move.type == MoveType.PROMOTION_NORMAL:
            p1.score += Piece.piece_value_dict[move.promotion]
            p1.add_piece(move.promotion)
            p1.remove_piece(PieceType.PAWN)

        if move.type == MoveType.PROMOTION_CAPTURE:
            p2.remove_piece(piece_captured.type)

        elif move.type == MoveType.CAPTURE:
            p1.score += piece_captured.value
            p2.remove_piece(piece_captured.type)

        elif move.type == MoveType.ENPASSANT:
            p1.score += 1
            p2.remove_piece(PieceType.PAWN)

    def play(self):
        """
        Function that runs the game loop
        """
        self.state = GameState.IN_PROGRESS
        self.validMoves = self.board.gen_valid_moves(self.turn)

        # Main game loop
        while(self.state == GameState.IN_PROGRESS):
            print(self.validMoves)
            self.board.print_board()

            # Read user move
            x = int(input())
            y = int(input())
            x2 = int(input())
            y2 = int(input())

            # Asks for another move ultil we get a valid one
            while not next((move for move in self.validMoves if (x,y,x2,y2) == move.coords), None):            
                x = int(input())
                y = int(input())
                x2 = int(input())
                y2 = int(input())

            moves = [m for m in self.validMoves if m.coords == (x,y,x2,y2)]
            
            # Checking if it's a promotions move
            if(len(moves) > 1):
                prom_piece = input()
                move = next(m for m in moves if m.promotion.value == prom_piece)
            else:
                move = moves[0]

            # Checking if it's a dead move
            self.deadMoves = (self.deadMoves + 1 
                              if self.board.board[x][y].type != PieceType.PAWN and move.type != MoveType.CAPTURE
                              else 0)

            if self.turn == PieceColor.WHITE:
                self._update_player_data(self.white,self.black,move)
            else:
                self._update_player_data(self.black,self.white,move)

            # Applies the move and checks if the game ended
            self.board._apply_move(move)
            self._change_turn()
            self.validMoves = self.board.gen_valid_moves(self.turn,move)

            self._update_state()

game = ChessGame()
game.play()
