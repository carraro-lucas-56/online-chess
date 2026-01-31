import numpy as np
import itertools
from enum import Enum
from dataclasses import dataclass

from .piece import Piece, PieceType, PieceColor, Move, MoveType, PIECE_VALUES
from .chessboard import ChessBoard
from .player import Player

class GameError(Exception):
    pass

class InvalidMove(GameError):
    pass

class GameNotInProgress(GameError):
    pass

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
    BK: bool = True
    BQ: bool = True
    WK: bool = True
    WQ: bool = True 
    enpassantSquare: tuple[int,int] | None = None
    pawn_promoted: Piece | None = None
    piece_captured: Piece | None = None
    deadMoves: int = 0
    lastMove: Move | None = None

class ChessGame():
    def __init__(self):
        self.turn = PieceColor.WHITE
        self.board = ChessBoard()
        self.white = Player(PieceColor.WHITE,board=self.board.board,time_left=600)
        self.black = Player(PieceColor.BLACK,board=self.board.board,time_left=600,robot=True)

        # List with all the valid moves current available for the colos who's playing in this turn
        self.validMoves = self.board.gen_valid_moves(self.turn,self.white.piecesLeft,self.black.piecesLeft,True,True)

        # Castling rights
        self.BK = True
        self.BQ = True
        self.WK = True
        self.WQ = True

        # Coords of a pawn that can be captured en passant
        self.enpassantSquare = None

        # Move count
        self.deadMoves = 0   
        self.totalMoves = 1

        # State attributes
        self.state = GameState.READY_TO_START
        self.snapshots = [GameSnapshot(validMoves=self.validMoves,state=self.state)]

        self.gen_random_attr_keys()
        self.init_zobrist()

    def _change_turn(self) -> None:
        self.turn = PieceColor.WHITE if self.turn == PieceColor.BLACK else PieceColor.BLACK

    def gen_random_attr_keys(self) -> None:
        """
        Assign random numbers for game attributes.
        """
        rng = np.random.default_rng(seed=1000)
        max = np.iinfo(np.uint64).max

        # Assigning random number for each combination of (square,piece,color)
        self.pieceSquareKeys = {}
        square_coords = [(x,y) for x in range(8) for y in range(8)]

        combs = itertools.product(square_coords,PieceType,PieceColor)
        
        for item in combs:
            self.pieceSquareKeys[item] = rng.integers(0,max,dtype=np.uint64)

        # Assigning random number to indicate if it's white playing
        self.whitePlayingKey = rng.integers(0,max,dtype=np.uint64)

        # Assigning random number for castling rights
        self.castlingKeys = {}
        for item in ["WK","WQ","BK","BQ"]:
            self.castlingKeys[item] = rng.integers(0,max,dtype=np.uint64)
        
        # Assigning random number for each file (usefull for en passant squares)
        self.enpassantKeys = {}
        for x in range(8):
            self.enpassantKeys[x] = rng.integers(0,max,dtype=np.uint64)

    def init_zobrist(self) -> np.uint64:
        """
        Applies an inital hash value to the game.
        """

        xor = np.uint64(0)

        for x in range(8):
            for y in range(8):
                piece = self.board.board[x][y]
                if piece:
                    xor ^= self.pieceSquareKeys[((x,y),piece.type,piece.color)]

        if self.turn == PieceColor.WHITE:
            xor ^= self.whitePlayingKey

        if self.WK:
            xor ^= self.castlingKeys["WK"]
        
        if self.WQ:
            xor ^= self.castlingKeys["WQ"]
        
        if self.BK:
            xor ^= self.castlingKeys["BK"]
        
        if self.BQ:
            xor ^= self.castlingKeys["BQ"]
        
        if self.enpassantSquare:
            xor ^= self.enpassantKeys[self.enpassantSquare[0]]

        self.zobristHash = xor

    def set_initial_setup(self) -> None:
        self.board.reset()
        self.white.reset(time_left=600)
        self.black.reset(time_left=600)
        self.turn = PieceColor.WHITE
        self.validMoves = self.board.gen_valid_moves(self.turn)
        self.snapshots = [GameSnapshot(validMoves=self.validMoves,
                                          state=self.state)]
        self.state = GameState.READY_TO_START
        self.BQ = True
        self.BK = True
        self.WQ = True
        self.WK = True
        self.enpassantSquare = None
        self.deadMoves = 0
        self.deadMoves = 1
        self.gen_random_attr_keys()
        self.init_zobrist()

    def start_game(self) -> None:
        if self.state != GameState.READY_TO_START:
            self.set_initial_setup()
        self.state = GameState.IN_PROGRESS

# =======================================================
# ----- HELPER FUNCTIONS TO UPDATE GAME ATTRIBUTES ------
# =======================================================

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

    def _update_state(self, search_mode: bool = False) -> None:
        """
        Functions that checks if the game ended.
        """

        player = self.black if self.turn == PieceColor.WHITE else self.white
        pieces = self.black.piecesLeft if self.turn == PieceColor.BLACK else self.white.piecesLeft

        if not self.validMoves:
            self.state = (GameState.CHACKMATE 
                          if self.board.is_checked(self.turn,pieces)
                          else GameState.STALEMATE)
        if search_mode:
            return    

        elif self.deadMoves == 75:
            self.state = GameState.DRAW_BY_75_MOVE_RULE
        elif self._insufficient_material():
            self.state = GameState.INSUFFICIENT_MATERIAL
        elif player.time_left <= 0:
            self.state = GameState.TIMEOUT

    def _update_player_data(self, pawn_promoted: Piece | None, piece_captured: Piece | None ,move: Move) -> None:
        """
        Updates players's data based on the provided move.
        
        p1 is the player who performed the move.
        We suppose that the move is valid.

        pawn_promoted is the piece that was in the origin square before the move was done.
        """

        (p1,p2) = ((self.white,self.black) if self.turn == PieceColor.WHITE 
                                           else (self.black,self.white))

        if(piece_captured):
            p1.add_captured_piece(piece_captured)
            p2.remove_piece(piece_captured)

        match move.type:
            case MoveType.PROMOTION_NORMAL | MoveType.PROMOTION_CAPTURE:
                prom_piece = self.board.board[move.coords[2]][move.coords[3]]
                p1.add_piece(prom_piece)
                p1.remove_piece(pawn_promoted)
                p1.score += PIECE_VALUES[move.promotion]-1
            case MoveType.CAPTURE | MoveType.ENPASSANT:
                p1.score += PIECE_VALUES[piece_captured.type]

    def _undo_player_data (self, pawn_promoted: Piece, piece_captured: Piece | None, move: Move) -> None:  
        """
        Updates player data after undoing the give move.

        piece_moved is the piece that was in the destination square BEFORE the move was undone in the board.
        """
        (p1,p2) = ((self.white,self.black) if self.turn == PieceColor.WHITE 
                                           else (self.black,self.white))

        if piece_captured:        
            p1.remove_captured_piece()
            p2.add_piece(piece_captured)

        match move.type:
            case MoveType.PROMOTION_NORMAL | MoveType.PROMOTION_CAPTURE:
                prom_piece = self.board.board[move.coords[2]][move.coords[3]]
                p1.remove_piece(prom_piece)
                p1.add_piece(pawn_promoted)
                p1.score -= PIECE_VALUES[move.promotion]-1
            case MoveType.CAPTURE | MoveType.ENPASSANT:
                p1.score -= PIECE_VALUES[piece_captured.type]

    def _update_castling_rights(self, move: Move) -> None:
        """
        Updates castlings rights based in the provided move.

        Checks if the current player is moving the  
        king/rook or capturing a opposing rook.
        """
        (x,y,x2,y2) = move.coords
        piece = self.board.board[x][y]

        if self.turn == PieceColor.WHITE:
            if (self.WK and (piece.type == PieceType.KING or (piece.type == PieceType.ROOK and y == 7))):
                self.WK = False

            if (self.WQ and (piece.type == PieceType.KING or (piece.type == PieceType.ROOK and y == 0))):
                self.WQ = False

            # Case when we are capturing the opponent's rook
            if (self.BK and (x2,y2) == (0,7)):
                self.BK = False
            
            elif (self.BK and (x2,y2) == (0,0)):
                self.BQ = False

        else:
            if (self.BK and (piece.type == PieceType.KING or (piece.type == PieceType.ROOK and y == 7))):
                self.BK = False

            if (self.BQ and (piece.type == PieceType.KING or (piece.type == PieceType.ROOK and y == 0))):
                self.BQ = False

            # Case when we are capturing the opponent's rook
            if (self.WK and (x2,y2) == (7,7)):
                self.WK = False
            
            elif (self.WK and (x2,y2) == (7,0)):
                self.WQ = False

    def update_hash(self) -> None:
        """
        Must be called after the given move is made.
        """
        new_hash = self.zobristHash

        curr_state = self.snapshots[-1]
        prev_state = self.snapshots[-2] # game state before the move was played

        move = curr_state.lastMove
        (x,y,x2,y2) = move.coords

        piece = self.board.board[x2][y2]
        piece_captured = curr_state.piece_captured

        match move.type:
            case MoveType.NORMAL:
                new_hash ^= self.pieceSquareKeys[((x,y),piece.type,piece.color)]
                new_hash ^= self.pieceSquareKeys[((x2,y2),piece.type,piece.color)]
            
            case MoveType.PROMOTION_CAPTURE | MoveType.PROMOTION_NORMAL:
                new_hash ^= self.pieceSquareKeys[((x,y),PieceType.PAWN,piece.color)]
                new_hash ^= self.pieceSquareKeys[((x2,y2),move.promotion,piece.color)]

                if move.type == MoveType.PROMOTION_CAPTURE:
                    new_hash ^= self.pieceSquareKeys[((x2,y2),piece_captured.type,piece_captured.color)]

            case MoveType.CAPTURE:
                new_hash ^= self.pieceSquareKeys[((x,y),piece.type,piece.color)]
                new_hash ^= self.pieceSquareKeys[((x2,y2),piece_captured.type,piece_captured.color)]
                new_hash ^= self.pieceSquareKeys[((x2,y2),piece.type,piece.color)]

            case MoveType.CASTLE:
                (r_col,aux) = (0,1) if y-y2 > 0 else (7,-1)

                new_hash ^= self.pieceSquareKeys[((x,r_col) ,PieceType.ROOK,piece.color)]         
                new_hash ^= self.pieceSquareKeys[((x,y2+aux),PieceType.ROOK,piece.color)]         
    
                new_hash ^= self.pieceSquareKeys[((x,y),piece.type,piece.color)]
                new_hash ^= self.pieceSquareKeys[((x2,y2),piece.type,piece.color)]

            case MoveType.ENPASSANT:
                new_hash ^= self.pieceSquareKeys[((x,y),piece.type,piece.color)]
                new_hash ^= self.pieceSquareKeys[((x,y2),PieceType.PAWN,piece.color)]         
                new_hash ^= self.pieceSquareKeys[((x2,y2),piece.type,piece.color)]

        if prev_state.WK != self.WK:
            new_hash ^= self.castlingKeys["WK"]
        
        if prev_state.WQ != self.WQ:
            new_hash ^= self.castlingKeys["WQ"]
        
        if prev_state.BK != self.BK:
            new_hash ^= self.castlingKeys["BK"]
        
        if prev_state.BQ != self.BQ:
            new_hash ^= self.castlingKeys["BQ"]
        
        if prev_state.enpassantSquare != self.enpassantSquare:
            if self.enpassantSquare is not None:
                new_hash ^= self.enpassantKeys[self.enpassantSquare[0]]
            if prev_state.enpassantSquare is not None:
                new_hash ^= self.enpassantKeys[prev_state.enpassantSquare[0]]

        new_hash ^= self.whitePlayingKey

        self.zobristHash = new_hash

# ========================================================
# ----- FUNCTIONS PERFORM AND UNDO MOVES IN THE GAME -----
# ========================================================

    def play_move(self, x: int, y: int, x2: int, y2: int, 
                  prom_piece: PieceType | None = None, 
                  search_mode=False, 
                  move_obj: Move | None = None) -> Move:
        """
        Validates and applies a move given by board coordinates.

        Handles promotion resolution, updates player clocks, applies the move
        to the board, switches turn, regenerates legal moves, and updates
        the game state.
        """
        
        if self.state != GameState.IN_PROGRESS:
            raise GameNotInProgress

        # Checking which move matches the given coordinates
        move = (move_obj if move_obj
                else next((m for m in self.validMoves if m.coords == (x,y,x2,y2) and m.promotion == prom_piece),None))

        if move is None:
            raise InvalidMove

        self._update_castling_rights(move)            
        
        move.coords = (x,y,x2,y2)
        piece_moved = self.board.board[x][y]

        # Checking if the move is a two square pawn advance
        if (piece_moved.type == PieceType.PAWN 
            and piece_moved.initial_row == x
            and abs(piece_moved.initial_row-x2)) == 2:
            self.enpassantSquare = (x2,y2) 
        else:
            self.enpassantSquare = None
                
        # Update 75-move rule counter
        self.deadMoves = (self.deadMoves + 1 
                          if self.board.board[x][y].type != PieceType.PAWN and move.type != MoveType.CAPTURE
                          else 0)
        
        if self.turn == PieceColor.BLACK:
            self.totalMoves += 1

        pawn_promoted, piece_captured = self.board.apply_move(move)
        
        self._update_player_data(pawn_promoted,piece_captured,move)

        self._change_turn()
        
        (pieces, oppsPieces, CK, CQ) = ((self.black.piecesLeft,self.white.piecesLeft,self.BK,self.BQ) 
                                         if self.turn == PieceColor.BLACK 
                                         else (self.white.piecesLeft,self.black.piecesLeft,self.WK,self.WQ))

        # s = time.perf_counter()
        self.validMoves = self.board.gen_valid_moves(self.turn,pieces,oppsPieces,CK,CQ,self.enpassantSquare)
        # e = time.perf_counter()
        # print(f"{(e-s):.5f}") 

        # Checks if the game ended
        self._update_state(search_mode=search_mode)


        self.snapshots.append(GameSnapshot(lastMove=move,
                                           deadMoves=self.deadMoves,
                                           validMoves=self.validMoves,
                                           state=self.state,
                                           BK=self.BK,
                                           BQ=self.BQ,
                                           WK=self.WK,
                                           WQ=self.WQ,
                                           enpassantSquare=self.enpassantSquare,
                                           pawn_promoted=pawn_promoted,
                                           piece_captured=piece_captured))

        self.update_hash()

    def unplay_move(self, pop: bool=True, search_mode: bool = False) -> None:
        """
        Restore the game overall state back to how it was before the last move played.
        """

        # there's no more moves to undo
        if len(self.snapshots) < 2:
            return 

        self.update_hash()

        self._change_turn()
        
        prev_state = self.snapshots[-2]

        self.BK = prev_state.BK 
        self.BQ = prev_state.BQ 
        self.WK = prev_state.WK 
        self.WQ = prev_state.WQ 

        move = self.snapshots[-1].lastMove

        piece_captured  = self.snapshots[-1].piece_captured
        
        pawn_promoted = self.snapshots[-1].pawn_promoted

        self.board.undo_move(move,pawn_promoted,piece_captured)

        self._undo_player_data(pawn_promoted,piece_captured,move)

        self.enpassantSquare = prev_state.enpassantSquare

        self.deadMoves = prev_state.deadMoves

        if self.turn == PieceColor.BLACK:
            self.totalMoves -= 1

        self.validMoves = prev_state.validMoves

        self.state = prev_state.state

        if pop:
            self.snapshots.pop()

if __name__ == "__main__":
    import time
    game = ChessGame()
    game.start_game()
    # s = time.perf_counter()
    game.play_move(6,4,4,4)
    # game.unplay_move()
    # e = time.perf_counter()
    # print(f"{(e-s):.5f} seg")