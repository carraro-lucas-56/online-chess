import queue
import threading
import logging
from enum import Enum

from .piece import Move, PieceColor, MoveType
from .chessgame import ChessGame, GameState
from utils.utils import flip_and_negate

logger = logging.getLogger(__name__)

PAWN_PST_WHITE = [
    80, 80, 80, 80, 80, 80, 80, 80,
    50, 50, 50, 50, 50, 50, 50, 50,
    10, 10, 20, 30, 30, 20, 10, 10,
     5,  5, 10, 25, 25, 10,  5,  5,
     0,  0,  0, 20, 20,  0,  0,  0,
     5, -5,-10,  0,  0,-10, -5,  5,
     5, 10, 10,-20,-20, 10, 10,  5,
     0,  0,  0,  0,  0,  0,  0,  0,
]

KNIGHT_PST_WHITE = [
   -50,-40,-30,-30,-30,-30,-40,-50,
   -40,-20,  0,  0,  0,  0,-20,-40,
   -30,  0, 10, 15, 15, 10,  0,-30,
   -30,  5, 15, 20, 20, 15,  5,-30,
   -30,  0, 15, 20, 20, 15,  0,-30,
   -30,  5, 10, 15, 15, 10,  5,-30,
   -40,-20,  0,  5,  5,  0,-20,-40,
   -50,-40,-30,-30,-30,-30,-40,-50,
]

BISHOP_PST_WHITE = [
   -20,-10,-10,-10,-10,-10,-10,-20,
   -10,  0,  0,  0,  0,  0,  0,-10,
   -10,  0,  5, 10, 10,  5,  0,-10,
   -10,  5,  5, 10, 10,  5,  5,-10,
   -10,  0, 10, 10, 10, 10,  0,-10,
   -10, 10, 10, 10, 10, 10, 10,-10,
   -10,  5,  0,  0,  0,  0,  5,-10,
   -20,-10,-10,-10,-10,-10,-10,-20,
]

ROOK_PST_WHITE = [
     0,  0,  0,  5,  5,  0,  0,  0,
    -5, 10, 10, 10, 10, 10, 10, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
     0,  0,  0,  0,  0,  0,  0,  0,
     0,  0,  0,  0,  0,  0,  0,  0,
]

QUEEN_PST_WHITE = [
   -20,-10,-10, -5, -5,-10,-10,-20,
   -10,  0,  0,  0,  0,  0,  0,-10,
   -10,  0,  5,  5,  5,  5,  0,-10,
    -5,  0,  5,  5,  5,  5,  0, -5,
     0,  0,  5,  5,  5,  5,  0, -5,
   -10,  5,  5,  5,  5,  5,  0,-10,
   -10,  0,  5,  0,  0,  0,  0,-10,
   -20,-10,-10, -5, -5,-10,-10,-20,
]

KING_PST_WHITE = [
   -30,-40,-40,-50,-50,-40,-40,-30,
   -30,-40,-40,-50,-50,-40,-40,-30,
   -30,-40,-40,-50,-50,-40,-40,-30,
   -30,-40,-40,-50,-50,-40,-40,-30,
   -20,-30,-30,-40,-40,-30,-30,-20,
   -10,-20,-20,-20,-20,-20,-20,-10,
    20, 20,  0,  0,  0,  0, 20, 20,
    20, 30, 10,  0,  0, 10, 30, 20,
]

PST = [
    # WHITE
    [
        PAWN_PST_WHITE,
        KNIGHT_PST_WHITE,
        BISHOP_PST_WHITE,
        ROOK_PST_WHITE,
        QUEEN_PST_WHITE,
        KING_PST_WHITE,
    ],
    # BLACK
    [
        flip_and_negate(PAWN_PST_WHITE),
        flip_and_negate(KNIGHT_PST_WHITE),
        flip_and_negate(BISHOP_PST_WHITE),
        flip_and_negate(ROOK_PST_WHITE),
        flip_and_negate(QUEEN_PST_WHITE),
        flip_and_negate(KING_PST_WHITE),
    ]
]

def move_score(move):
    if move.type == MoveType.PROMOTION_CAPTURE or move.type == MoveType.PROMOTION_NORMAL:

        return 3
    if move.type == MoveType.CASTLE:
        return 1
    if move.type == MoveType.CAPTURE: 
        return 2

    return 0

class BoundType(Enum):
    UPPER = 0
    LOWER = 1
    EXACT = 2

class Engine:
    def __init__(self):
        self.MAX_DEPTH = 4
        self.TT = {}
        self.nodes_visited = 0  
        self.thread = None 
        self.stop_event = threading.Event() 
        self.thinking = threading.Event()
        self.queue = queue.Queue()
        self.PST = [
        # WHITE
        [
            PAWN_PST_WHITE,
            KNIGHT_PST_WHITE,
            BISHOP_PST_WHITE,
            ROOK_PST_WHITE,
            QUEEN_PST_WHITE,
            KING_PST_WHITE,
        ],
        # BLACK
        [
            flip_and_negate(PAWN_PST_WHITE),
            flip_and_negate(KNIGHT_PST_WHITE),
            flip_and_negate(BISHOP_PST_WHITE),
            flip_and_negate(ROOK_PST_WHITE),
            flip_and_negate(QUEEN_PST_WHITE),
            flip_and_negate(KING_PST_WHITE),
        ]
]

    def alpha_beta_root(self,game: ChessGame, isMax: bool, max_depth: int ,alpha = -1000000, beta = 1000000) -> Move:
        try:
            (_, tt_move, _, _) = self.TT[game.zobristHash]
        except:
            tt_move = None

        orig_beta = beta
        orig_alpha = alpha

        moves = sorted(game.validMoves, key=move_score, reverse=True)

        if tt_move and tt_move in moves:
            moves.remove(tt_move)
            moves.insert(0, tt_move)

        for move in moves:
            game.play_move(move,search_mode=True)
            score = self.alpha_beta(game, alpha, beta, 1, not isMax, max_depth=max_depth)

            if isMax and score > alpha:
                alpha = score
                tt_move = move
            elif not isMax and score < beta:
                beta = score
                tt_move = move

            game.unplay_move(search_mode=True)

            if alpha >= beta:
                break

        score = alpha if isMax else beta

        if score <= orig_alpha:
            bound = BoundType.UPPER
        elif score >= orig_beta:
            bound = BoundType.LOWER
        else:
            bound = BoundType.EXACT

        self.TT[game.zobristHash] = (score,tt_move,max_depth,bound)    
        
        if max_depth == self.MAX_DEPTH:
            logger.info(f"{self.nodes_visited} nodes visited in the last search")
            self.nodes_visited = 0
        
        return tt_move

    def alpha_beta(self,game: ChessGame, alpha: int, beta: int, depth: int, isMax: bool, max_depth: int) -> int: 
        self.nodes_visited += 1

        try:
            (s,tt_move,d,b) = self.TT[game.zobristHash]
            if d >= max_depth-depth:
                match b:
                    case BoundType.EXACT:
                        return s
                    case BoundType.LOWER:
                        alpha = s
                    case BoundType.UPPER:
                        beta = s

                if alpha >= beta:
                    return alpha if isMax else beta
        except:
            tt_move = None

        if depth == max_depth or game.state != GameState.IN_PROGRESS:
            return self.eval_position(game)

        orig_beta = beta
        orig_alpha = alpha

        moves = sorted(game.validMoves, key=move_score, reverse=True)

        if tt_move and tt_move in moves:
            moves.remove(tt_move)
            moves.insert(0, tt_move)

        for move in moves:    
            game.play_move(move,search_mode=True)
            score = self.alpha_beta(game, alpha, beta, depth+1, not isMax, max_depth=max_depth)

            if isMax and score > alpha:
                alpha = score
                tt_move = move
            elif not isMax and score < beta:
                beta = score 
                tt_move = move

            game.unplay_move(search_mode=True)

            if alpha >= beta:
                break

        score = alpha if isMax else beta

        if score <= orig_alpha:
            bound = BoundType.UPPER
        elif score >= orig_beta:
            bound = BoundType.LOWER
        else:
            bound = BoundType.EXACT

        self.TT[game.zobristHash] = (score,tt_move,max_depth-depth,bound)    

        return score

    def eval_position(self, game: ChessGame) -> int:

        if game.state == GameState.CHACKMATE:
            return 100000 if game.turn == PieceColor.BLACK else -100000
        elif game.state != GameState.IN_PROGRESS:
            return 0

        score = 0

        material_advantage = (game.white.score - game.black.score)*100

        pieces = game.black.piecesLeft if game.turn == PieceColor.BLACK else game.white.piecesLeft

        isChecked = 30 if game.board.is_checked(game.turn,pieces) else 0

        score += material_advantage + (-isChecked if game.turn == PieceColor.WHITE else isChecked)

        for piece in game.white.piecesLeft:
            (x,y) = piece.position
            score += self.PST[0][piece.type.value-1][x*8 + y]          

        for piece in game.black.piecesLeft:
            (x,y) = piece.position
            score += self.PST[1][piece.type.value-1][x*8 + y]          

        return score    

    def start_thread(self, snapshot: ChessGame):
        self.thread = threading.Thread(target=self.gen_best_move,
                                              args=[snapshot],
                                              daemon=True)
        self.thread.start()

    def gen_best_move(self, game_snapshot: ChessGame) -> None:
        """
        Trigger alpha beta pruning algorithm and put the generated move into the engine's queue.
        """

        self.thinking.set()

        try:
            if self.stop_event.is_set():
                return

            for depth in range(1,self.MAX_DEPTH+1):
                engine_move = self.alpha_beta_root(game_snapshot,game_snapshot.turn==PieceColor.WHITE,max_depth=depth)

            if self.stop_event.is_set():
                return

            self.queue.put(engine_move)
            
        except Exception as e:
            logger.error(f"Engine Therad crashed {e}")

        finally:
            self.thinking.clear()
