from src.piece import Move, PieceColor, MoveType
from src.chessgame import ChessGame, GameState

MAX_DEPTH = 3

def alpha_beta_root(game: ChessGame,  isMax: bool, alpha = -100000, beta = 1000000) -> Move:
    bestMove = None 
    
    for move in game.validMoves:
        piece_prev_state = game.board.board[move.coords[0]][move.coords[1]].state

        piece_captured = (game.board.board[move.coords[2]][move.coords[3]] 
                          if move.type != MoveType.ENPASSANT 
                          else game.board.board[move.coords[0]][move.coords[3]]) 

        prev_dead_moves_cnt = game.deadMoves
        prev_valid_moves = game.validMoves
        prev_state = game.state

        game.play_move(*move.coords,save=False)
        score = alpha_beta(game, alpha, beta, 1, not isMax)

        if isMax:
            if score > alpha:
                alpha = score
                bestMove = move
        else:
            if score < beta:
                beta = score
                bestMove = move

        game.unplay_move_inplace(lastMove=move,
                                 piece_captured=piece_captured,
                                 piece_prev_state=piece_prev_state,
                                 prev_valid_moves=prev_valid_moves,
                                 prev_dead_moves_cnt=prev_dead_moves_cnt,
                                 prev_state=prev_state)

        if alpha >= beta:
            break

    return bestMove


def alpha_beta(game: ChessGame, alpha: int, beta: int, depth: int, isMax: bool) -> int: 
    
    if depth == MAX_DEPTH or game.state != GameState.IN_PROGRESS:
        return eval(game)
    
    for move in game.validMoves:
        piece_prev_state = game.board.board[move.coords[0]][move.coords[1]].state
    
        piece_captured = (game.board.board[move.coords[2]][move.coords[3]] 
                        if move.type != MoveType.ENPASSANT 
                        else game.board.board[move.coords[0]][move.coords[3]]) 
    
        prev_dead_moves_cnt = game.deadMoves
        prev_valid_moves = game.validMoves
        prev_state = game.state

        game.play_move(*move.coords,save=False)
        score = alpha_beta(game, alpha, beta, depth+1, not isMax)

        if isMax:
            if score > alpha:
                alpha = score 
        else:
            if score < beta:
                beta = score 

        game.unplay_move_inplace(lastMove=move,
                                 piece_captured=piece_captured,
                                 piece_prev_state=piece_prev_state,
                                 prev_valid_moves=prev_valid_moves,
                                 prev_dead_moves_cnt=prev_dead_moves_cnt,
                                 prev_state=prev_state)

        if alpha >= beta:
            break

    return alpha if isMax else beta


def eval(game: ChessGame) -> int:
    material_advantage =  game.white.score - game.black.score

    match game.state:
        case GameState.IN_PROGRESS:
            return material_advantage
        case GameState.CHACKMATE:
            return 10000 if game.turn == PieceColor.BLACK else -10000
        case _:
            return 0