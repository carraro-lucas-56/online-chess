from enum import Enum

from .piece import Move, PieceColor, MoveType
from .chessgame import ChessGame, GameState

class BoundType(Enum):
    UPPER = 0
    LOWER = 1
    EXACT = 2

MAX_DEPTH = 3

TT = {}

def move_score(move):
    if move.type == MoveType.CASTLE:
        return 1500
    if move.type == MoveType.CAPTURE or move.type == MoveType.PROMOTION_CAPTURE: 
        return 1000
    return 0

def alpha_beta_root(game: ChessGame,  isMax: bool, alpha = -1000000, beta = 1000000) -> Move:
    bestMove = None 

    moves = sorted(game.validMoves, key=move_score, reverse=True)

    orig_beta = beta
    orig_alpha = alpha

    for move in moves:
        game.play_move(*move.coords,move.promotion,move_obj=move,search_mode=True)
        score = alpha_beta(game, alpha, beta, 1, not isMax)

        if isMax and score > alpha:
            alpha = score
            bestMove = move
        elif not isMax and score < beta:
            beta = score
            bestMove = move

        game.unplay_move()

        if alpha >= beta:
            break

    score = alpha if isMax else beta

    if score <= orig_alpha:
        bound = BoundType.UPPER
    elif score >= orig_beta:
        bound = BoundType.LOWER
    else:
        bound = BoundType.EXACT

    TT[game.zobristHash] = (score,MAX_DEPTH,bound)    

    return bestMove

def alpha_beta(game: ChessGame, alpha: int, beta: int, depth: int, isMax: bool) -> int: 
    try:
        (s,d,b) = TT[game.zobristHash]
        if d >= depth:
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
        pass

    if depth == MAX_DEPTH or game.state != GameState.IN_PROGRESS:
        return eval(game)

    orig_beta = beta
    orig_alpha = alpha

    moves = sorted(game.validMoves, key=move_score, reverse=True)

    for move in moves:        
        game.play_move(*move.coords,move.promotion,move_obj=move,search_mode=True)
        score = alpha_beta(game, alpha, beta, depth+1, not isMax)

        if isMax and score > alpha:
            alpha = score 
        elif not isMax and score < beta:
            beta = score 

        game.unplay_move()
        
        if alpha >= beta:
            break
            
    score = alpha if isMax else beta

    if score <= orig_alpha:
        bound = BoundType.UPPER
    elif score >= orig_beta:
        bound = BoundType.LOWER
    else:
        bound = BoundType.EXACT

    TT[game.zobristHash] = (score,MAX_DEPTH-depth,bound)    

    return score

def eval(game: ChessGame) -> int:

    if game.state == GameState.CHACKMATE:
        return 10000 if game.turn == PieceColor.BLACK else -10000
    elif game.state != GameState.IN_PROGRESS:
        return 0

    material_advantage = (game.white.score - game.black.score)*100
    mobility = len(game.validMoves)
    isChecked = 30 if game.board.is_checked(game.turn) else 0

    score = (material_advantage + mobility - isChecked 
             if game.turn == PieceColor.WHITE 
             else material_advantage - mobility + isChecked)
    
    return score    
