from src.piece import Move, PieceColor, MoveType
from src.chessgame import ChessGame, GameState

MAX_DEPTH = 2

def min_max_root(game: ChessGame) -> Move:
    bestMove = None 
    
    if game.turn == PieceColor.WHITE:
        highest = -100000
        
        for move in game.validMoves:
            piece_prev_state = game.board.board[move.coords[0]][move.coords[1]].state

            piece_captured = (game.board.board[move.coords[2]][move.coords[3]] 
                              if move.type != MoveType.ENPASSANT 
                              else game.board.board[move.coords[0]][move.coords[3]]) 

            prev_dead_moves_cnt = game.deadMoves
            prev_valid_moves = game.validMoves
            prev_state = game.state

            game.play_move(*move.coords,save=False)
            score = min_max(game, 1, False)

            if score > highest:
                highest = score 
                bestMove = move

            game.unplay_move_inplace(lastMove=move,
                                     piece_captured=piece_captured,
                                     piece_prev_state=piece_prev_state,
                                     prev_valid_moves=prev_valid_moves,
                                     prev_dead_moves_cnt=prev_dead_moves_cnt,
                                     prev_state=prev_state)
    else:
        smaller = +100000
        
        for move in game.validMoves:
            piece_prev_state = game.board.board[move.coords[0]][move.coords[1]].state

            piece_captured = (game.board.board[move.coords[2]][move.coords[3]] 
                              if move.type != MoveType.ENPASSANT 
                              else game.board.board[move.coords[0]][move.coords[3]]) 

            prev_dead_moves_cnt = game.deadMoves
            prev_valid_moves = game.validMoves
            prev_state = game.state

            game.play_move(*move.coords,save=False)
            score = min_max(game, 1, True)

            if score < smaller:
                smaller = score 
                bestMove = move

            game.unplay_move_inplace(lastMove=move,
                                     piece_captured=piece_captured,
                                     piece_prev_state=piece_prev_state,
                                     prev_valid_moves=prev_valid_moves,
                                     prev_dead_moves_cnt=prev_dead_moves_cnt,
                                     prev_state=prev_state)


    return bestMove


def min_max(game: ChessGame, depth: int, isMax: bool) -> int: 
    
    if depth == MAX_DEPTH or game.state != GameState.IN_PROGRESS:
        return eval(game)
    
    highest = -100000
    smaller =  100000

    for move in game.validMoves:
        piece_prev_state = game.board.board[move.coords[0]][move.coords[1]].state
    
        piece_captured = (game.board.board[move.coords[2]][move.coords[3]] 
                          if move.type != MoveType.ENPASSANT 
                          else game.board.board[move.coords[0]][move.coords[3]]) 
    
        prev_dead_moves_cnt = game.deadMoves
        prev_valid_moves = game.validMoves
        prev_state = game.state

        game.play_move(*move.coords,save=False)
        score = min_max(game, depth+1, not isMax)
        
        if score > highest:
            highest = score 
        if score < smaller:
            smaller = score

        game.unplay_move_inplace(lastMove=move,
                                 piece_captured=piece_captured,
                                 piece_prev_state=piece_prev_state,
                                 prev_valid_moves=prev_valid_moves,
                                 prev_dead_moves_cnt=prev_dead_moves_cnt,
                                 prev_state=prev_state)
        
    return highest if isMax else smaller


def eval(game: ChessGame) -> int:
    material_advantage =  game.white.score - game.black.score

    match game.state:
        case GameState.IN_PROGRESS:
            return material_advantage
        case GameState.CHACKMATE:
            return 10000 if game.turn == PieceColor.BLACK else -10000
        case _:
            return 0