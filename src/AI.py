from .piece import Move, PieceColor, MoveType, PieceType
from .chessgame import ChessGame, GameState

MAX_DEPTH = 3

def move_score(move):
    if move.type == MoveType.CASTLE:
        return 1500
    if move.type == MoveType.CAPTURE or move.type == MoveType.PROMOTION_CAPTURE: 
        return 1000
    return 0

def alpha_beta_root(game: ChessGame,  isMax: bool, alpha = -100000, beta = 1000000) -> Move:
    bestMove = None 

    moves = sorted(game.validMoves, key=move_score, reverse=True)

    for move in moves:
        game.play_move(*move.coords,move.promotion,search_mode=True) #,save=False)
        score = alpha_beta(game, alpha, beta, 1, not isMax)

        if isMax:
            if score > alpha:
                alpha = score
                bestMove = move
        else:
            if score < beta:
                beta = score
                bestMove = move

        game.unplay_move()

        if alpha >= beta:
            break

    return bestMove

def alpha_beta(game: ChessGame, alpha: int, beta: int, depth: int, isMax: bool) -> int: 
    
    if depth == MAX_DEPTH or game.state != GameState.IN_PROGRESS:
        return eval(game)

    moves = sorted(game.validMoves, key=move_score, reverse=True)

    for move in moves:
        game.play_move(*move.coords,move.promotion,search_mode=True) # ,save=False)    
        score = alpha_beta(game, alpha, beta, depth+1, not isMax)

        if isMax:
            if score > alpha:
                alpha = score 
        else:
            if score < beta:
                beta = score 

        game.unplay_move()
        
        if alpha >= beta:
            break
        
    return alpha if isMax else beta

def eval(game: ChessGame) -> int:

    if game.state == GameState.CHACKMATE:
        return 10000 if game.turn == PieceColor.BLACK else -10000
    elif game.state != GameState.IN_PROGRESS:
        return 0

    material_advantage = (game.white.score - game.black.score)*100
    mobility = len(game.validMoves)
    isChecked = 30 if game.board.is_checked(game.turn) else 0

    # score = material_advantage - mobility
    score = (material_advantage + mobility - isChecked 
             if game.turn == PieceColor.WHITE 
             else material_advantage - mobility + isChecked)
    
    return score    
