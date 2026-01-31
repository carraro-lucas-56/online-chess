from enum import Enum
from functools import reduce

from .piece import Move, PieceColor, MoveType, PIECE_VALUES, is_capture
from .chessgame import ChessGame, GameState

class BoundType(Enum):
    UPPER = 0
    LOWER = 1
    EXACT = 2

def move_score(move):
    if move.type == MoveType.PROMOTION_CAPTURE or move.type == MoveType.PROMOTION_NORMAL:
        return 3
    if move.type == MoveType.CASTLE:
        return 1
    if move.type == MoveType.CAPTURE: 
        return 2

    return 0

class Engine:
    def __init__(self):
        self.MAX_DEPTH = 4
        self.TT = {}
        self.nodes_visited = 0    

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
            game.play_move(*move.coords,move.promotion,move_obj=move,search_mode=True)
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
            print(self.nodes_visited)
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
            return self.eval(game)

        orig_beta = beta
        orig_alpha = alpha

        moves = sorted(game.validMoves, key=move_score, reverse=True)

        if tt_move and tt_move in moves:
            moves.remove(tt_move)
            moves.insert(0, tt_move)

        for move in moves:    

            game.play_move(*move.coords,move.promotion,move_obj=move,search_mode=True)
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

    @staticmethod
    def eval(game: ChessGame) -> int:

        if game.state == GameState.CHACKMATE:
            return 100000 if game.turn == PieceColor.BLACK else -100000
        elif game.state != GameState.IN_PROGRESS:
            return 0

        material_advantage = (game.white.score - game.black.score)*100
        mobility = len(game.validMoves)

        pieces = game.black.piecesLeft if game.turn == PieceColor.BLACK else game.white.piecesLeft

        isChecked = 30 if game.board.is_checked(game.turn,pieces) else 0

        score = (material_advantage + mobility - isChecked 
                 if game.turn == PieceColor.WHITE 
                 else material_advantage - mobility + isChecked)

        return score    
