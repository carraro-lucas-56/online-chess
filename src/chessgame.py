from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING
from dataclasses import dataclass

from .piece import PieceType, PieceState, PieceColor, MoveType, PIECE_VALUES
from .chessboard import ChessBoard
from .player import Player

if TYPE_CHECKING:
    import numpy as np
    from src.piece import Piece, Move

class GameState(Enum):
    IN_PROGRESS = 1
    CHACKMATE = 2
    STALEMATE = 3
    DRAW_BY_75_MOVE_RULE = 4
    INSUFFICIENT_MATERIAL = 5
    TIMEOUT = 6
    READY_TO_START = 7

@dataclass(frozen=True)
class GameSnapshot:
    validMoves: list[Move]
    state: GameState 
    board: np.ndarray | None
    deadMoves: int = 0
    piece_prev_state: PieceState = None
    piece_captured: Piece | None = None
    lastMove: Move = None

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
        self.stateHistory = [GameSnapshot(validMoves=self.validMoves,
                                          state=self.state,
                                          board=self.board.board)]
        self.deadMoves = 0   
        self.totalMoves = 1

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

    def _update_player_data(self,move: Move) -> None:
        """
        Updates players's data based on the provided move.
        
        p1 is the player who will perform the move.
        We suppose that the move is valid.
        """

        (p1,p2) = ((self.white,self.black) if self.turn == PieceColor.WHITE 
                                           else (self.black,self.white))

        piece_captured = (self.board.board[move.coords[0]][move.coords[3]] 
                          if move.type == MoveType.ENPASSANT 
                          else self.board.board[move.coords[2]][move.coords[3]])
        
        if(piece_captured):
            p1.add_captured_piece(piece_captured.type)
            p2.remove_piece(piece_captured.type)

        match move.type:
            case MoveType.PROMOTION_NORMAL | MoveType.PROMOTION_CAPTURE:
                p1.add_piece(move.promotion)
                p1.remove_piece(PieceType.PAWN)
                p1.score += PIECE_VALUES[move.promotion]-1
            case MoveType.CAPTURE | MoveType.ENPASSANT:
                p1.score += PIECE_VALUES[piece_captured.type]

    def _undo_player_data (self, move: Move, piece_captured: Piece | None = None) -> None:  

        (p1,p2) = ((self.white,self.black) if self.turn == PieceColor.WHITE 
                                           else (self.black,self.white))

        if piece_captured:        
            p1.remove_captured_piece()
            p2.add_piece(piece_captured.type)

        match move.type:
            case MoveType.PROMOTION_NORMAL | MoveType.PROMOTION_CAPTURE:
                p1.add_piece(PieceType.PAWN)
                p1.remove_piece(move.promotion)
                p1.score -= PIECE_VALUES[move.promotion]-1
            case MoveType.CAPTURE | MoveType.ENPASSANT:
                p1.score -= PIECE_VALUES[piece_captured.type]

    def set_initial_setup(self) -> None:
        self.board.reset()
        self.white.reset(time_left=600)
        self.black.reset(time_left=600)
        self.turn = PieceColor.WHITE
        self.validMoves = self.board.gen_valid_moves(self.turn)
        self.stateHistory = [GameSnapshot(validMoves=self.validMoves,
                                          state=self.state,
                                          board=self.board.board)]
        self.state = GameState.READY_TO_START
        self.deadMoves = 0
        self.deadMoves = 1

    def start_game(self) -> None:
        if self.state != GameState.READY_TO_START:
            self.set_initial_setup()
        self.state = GameState.IN_PROGRESS

    def play_move(self, x: int, y: int, x2: int, y2: int, prom_piece: PieceType | None = None, search_mode=False) -> Move:
        """
        Validates and applies a move given by board coordinates.

        Handles promotion resolution, updates player clocks, applies the move
        to the board, switches turn, regenerates legal moves, and updates
        the game state.
        """
        
        if self.state != GameState.IN_PROGRESS:
            raise GameNotInProgress

        # Checking which moves matches the given coordinates
        move = next((m for m in self.validMoves if m.coords == (x,y,x2,y2) and m.promotion == prom_piece),None)

        if move is None:
            raise InvalidMove

        piece_prev_state = self.board.board[move.coords[0]][move.coords[1]].state
            
        self._update_player_data(move)
        
        # Update 75-move rule counter
        self.deadMoves = (self.deadMoves + 1 
                          if self.board.board[x][y].type != PieceType.PAWN and move.type != MoveType.CAPTURE
                          else 0)
        
        if self.turn == PieceColor.BLACK:
            self.totalMoves += 1

        piece_captured = self.board.apply_move(move)
        self._change_turn()
        
        self.validMoves = self.board.gen_valid_moves(self.turn,move)
        self._update_state()

        self.stateHistory.append(GameSnapshot(lastMove=move,
                                              deadMoves=self.deadMoves,
                                              validMoves=self.validMoves,
                                              board=None if search_mode else self.board.board.copy(),
                                              state=self.state,
                                              piece_captured=piece_captured,
                                              piece_prev_state=piece_prev_state))

    def unplay_move(self, pop: bool=True) -> None:
        """
        Undo the last move done in the game.
        """

        # there's no more moves to undo
        if len(self.stateHistory) < 2:
            return 

        self._change_turn()
        
        prev_state = self.stateHistory[-2]

        move = self.stateHistory[-1].lastMove
        piece_old_state = self.stateHistory[-1].piece_prev_state
        piece_captured  = self.stateHistory[-1].piece_captured

        self.board.undo_move(move,piece_captured,piece_old_state)

        self.deadMoves = prev_state.deadMoves

        if self.turn == PieceColor.BLACK:
            self.totalMoves -= 1

        self.validMoves = prev_state.validMoves
        
        self._undo_player_data(move,piece_captured)

        self.state = prev_state.state

        if pop:
            self.stateHistory.pop()

    def unplay_move_inplace(self,
                            lastMove: Move, 
                            piece_captured: Piece,
                            piece_prev_state: PieceState,
                            prev_valid_moves: list[Move],
                            prev_dead_moves_cnt: int,
                            prev_state: GameState
                            ):
        
        self.board.undo_move(lastMove,piece_captured,piece_prev_state)

        self._change_turn()

        self._undo_player_data(lastMove,piece_captured)

        self.validMoves = prev_valid_moves

        if self.turn == PieceColor.BLACK:
            self.totalMoves -= 1

        self.deadMoves = prev_dead_moves_cnt

        self.state = prev_state
