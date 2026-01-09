from src.chessboard import *
from src.piece import *
from src.player import *
import time
import random

class GameState(Enum):
    IN_PROGRESS = 1
    CHACKMATE = 2
    STALEMATE = 3
    DRAW_BY_75_MOVE_RULE = 4
    INSUFFICIENT_MATERIAL = 5
    TIMEOUT = 6
    READY_TO_START = 7

class GameError(Exception):
    pass

class InvalidMove(GameError):
    pass

class GameNotInProgress(GameError):
    pass

class ChessGame():
    def __init__(self):
        self.turn = PieceColor.WHITE
        self.board = ChessBoard()
        self.state = GameState.READY_TO_START
        self.white = Player(PieceColor.WHITE,time_left=600)
        self.black = Player(PieceColor.BLACK,time_left=600,robot=True)
        self.validMoves = self.board.gen_valid_moves(self.turn) # List with all the valid moves current available for the colos who's playing in this turn 
        self.deadMoves = 0   

    def _change_turn(self) -> None:
        self.turn = PieceColor.WHITE if self.turn == PieceColor.BLACK else PieceColor.BLACK

    def _insufficient_material(self) -> bool:
        """
        Return True if no checkmate is possible at all, even with cooperation.
        """

        set_W = set(self.white.piecesLeft)
        set_B = set(self.black.piecesLeft)

        # Insufficient material combinations
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


        # King + any number of same color bishops
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
        """
        Functions that checks if the game ended.
        """

        player = self.black if self.turn == PieceColor.WHITE else self.white
        
        if not self.validMoves:
            self.state = (GameState.CHACKMATE 
                          if self.board.is_checked(self.turn)
                          else GameState.STALEMATE)
        elif self.deadMoves == 75:
            self.state = GameState.DRAW_BY_75_MOVE_RULE
        elif self._insufficient_material():
            self.state = GameState.INSUFFICIENT_MATERIAL
        elif player.time_left <= 0:
            self.state = GameState.TIMEOUT

    def _update_player_data(self,move: Move, turn_start_time: float) -> None:
        """
        Updates players's data based on the provided move.
        
        p1 is the player who will perform the move.
        We suppose that the move is valid.
        """

        (p1,p2) = ((self.white,self.black) if self.turn == PieceColor.WHITE 
                                           else (self.black,self.white))

        # p1.time_left = p1.time_left - (time.monotonic() - turn_start_time)

        # There's no more player data to update after a regular move or castling move
        if move.type == MoveType.NORMAL or move.type == MoveType.CASTLE:
            return

        piece_captured = self.board.board[move.coords[2]][move.coords[3]] # Might be None depending on the move type

        if move.type == MoveType.PROMOTION_CAPTURE or move.type == MoveType.PROMOTION_NORMAL:
            p1.score += Piece.piece_value_dict[move.promotion]-1
            p1.add_piece(move.promotion)
            p1.remove_piece(PieceType.PAWN)

        if move.type == MoveType.ENPASSANT:
            p1.score += 1
            p2.remove_piece(PieceType.PAWN)

        elif move.type != MoveType.PROMOTION_NORMAL:
            p1.score += 0 if move.type == MoveType.PROMOTION_CAPTURE else piece_captured.value
            p2.remove_piece(piece_captured.type)

    def set_initial_setup(self):
        """
        Sets the game back to it's inital state.
        """

        self.board.reset()
        self.white.reset(time_left=600)
        self.black.reset(time_left=600)
        self.turn = PieceColor.WHITE
        self.validMoves = self.board.gen_valid_moves(self.turn)
        self.state = GameState.READY_TO_START
        self.deadMoves = 0

    def start_game(self):
        if self.state != GameState.READY_TO_START:
            self.set_initial_setup()
        self.state = GameState.IN_PROGRESS

    def toggle_robot_move(self):
        if not self.validMoves:
            return 

        random_integer = random.randint(0, len(self.validMoves)-1)
        move = self.validMoves[random_integer]

        if move.type == MoveType.PROMOTION_CAPTURE or move.type == MoveType.PROMOTION_NORMAL:
            self.play_move(*move.coords,move.promotion)
        else:
            self.play_move(*move.coords)

    def play_move(self, x: int, y: int, x2: int, y2: int, prom_piece: PieceType | None = None) -> None:
        """
        Validates and applies a move given by board coordinates.

        Handles promotion resolution, updates player clocks, applies the move
        to the board, switches turn, regenerates legal moves, and updates
        the game state.
        """
        
        turn_start_time = time.monotonic()

        if self.state != GameState.IN_PROGRESS:
            raise GameNotInProgress

        # Checking which moves matches the given coordinates
        moves = [m for m in self.validMoves if m.coords == (x,y,x2,y2)]
        
        if not moves:
            raise InvalidMove

        # Checking if it's a promotion move
        if(len(moves) > 1):
            move = next(m for m in moves if m.promotion == prom_piece)
        else:
            move = moves[0]

        self._update_player_data(move,turn_start_time)
        
        # Update 75-move rule counter
        self.deadMoves = (self.deadMoves + 1 
                          if self.board.board[x][y].type != PieceType.PAWN and move.type != MoveType.CAPTURE
                          else 0)
        
        self.board._apply_move(move)
        self._change_turn()

        self.validMoves = self.board.gen_valid_moves(self.turn,move)
        
        self._update_state()

        return move

    def can_toggle_promotion(self, x: int, y: int, x2: int, y2: int) -> bool:
        """
        Recives the origin coord from a move and checks if the move can toggle.

        a promotion, i.e the coord has a pawn that's one rank away from promoting. 
        """
        if x < 0 or x > 7 or y < 0 or y > 7:
            return False
        
        elif not next((move for move in self.validMoves if move.coords == (x,y,x2,y2)), None):
            return False

        row = 1 if self.turn == PieceColor.WHITE else 6

        return (x == row 
                and self.board.board[x][y] 
                and self.board.board[x][y].color == self.turn 
                and self.board.board[x][y].type == PieceType.PAWN) 

# game = ChessGame()
# game.start_game()
# game.play_move(6,4,4,4)
# game.play_move(1,4,3,4)
# game.board.print_board()