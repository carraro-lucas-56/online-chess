from enum import Enum

from .piece import Move, PieceColor, MoveType
from .chessgame import ChessGame, GameState

class BoundType(Enum):
    UPPER = 0
    LOWER = 1
    EXACT = 2

def move_score(move):
    if move.type == MoveType.PROMOTION_CAPTURE or move.type == MoveType.PROMOTION_NORMAL:
        return 2000
    if move.type == MoveType.CASTLE:
        return 1500
    if move.type == MoveType.CAPTURE: 
        return 1000

    return 0

class Engine:
    def __init__(self):
        self.MAX_DEPTH = 4
        self.TT = {}
        self.nodes_visited = 0    

    def alpha_beta_root(self,game: ChessGame,  isMax: bool, alpha = -1000000, beta = 1000000) -> Move:
        try:
            (s,bestMove,d,b) = self.TT[game.zobristHash]
            if d == 0:
                match b:
                    case BoundType.EXACT:
                        return bestMove
                    case BoundType.LOWER:
                        alpha = s
                    case BoundType.UPPER:
                        beta = s

                if alpha >= beta:
                    return bestMove
        except:
            bestMove = None

        moves = sorted(game.validMoves, key=move_score, reverse=True)

        orig_beta = beta
        orig_alpha = alpha

        foundIt = False if bestMove else True

        for move in moves:
            if move != bestMove and not foundIt:
                continue
            if move == bestMove:
                foundIt = True

            game.play_move(*move.coords,move.promotion,move_obj=move,search_mode=True)
            score = self.alpha_beta(game, alpha, beta, 1, not isMax)

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

        self.TT[game.zobristHash] = (score,0,bound)    
        
        print(self.nodes_visited)
        self.nodes_visited = 0
        
        return bestMove

    def alpha_beta(self,game: ChessGame, alpha: int, beta: int, depth: int, isMax: bool) -> int: 
        self.nodes_visited += 1

        try:
            (s,bestMove,d,b) = self.TT[game.zobristHash]
            if d <= depth:
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
            bestMove = None

        if depth == self.MAX_DEPTH or game.state != GameState.IN_PROGRESS:
            return self.eval(game)

        orig_beta = beta
        orig_alpha = alpha

        moves = sorted(game.validMoves, key=move_score, reverse=True)
        
        foundIt = False if bestMove else True

        for move in moves:    
            # start searching after the best move    
            if move != bestMove and not foundIt:
                continue
            if move == bestMove:
                foundIt = True

            game.play_move(*move.coords,move.promotion,move_obj=move,search_mode=True)
            score = self.alpha_beta(game, alpha, beta, depth+1, not isMax)

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

        self.TT[game.zobristHash] = (score,bestMove,depth,bound)    

        return score

    @staticmethod
    def eval(game: ChessGame) -> int:

        if game.state == GameState.CHACKMATE:
            return 100000 if game.turn == PieceColor.BLACK else -100000
        elif game.state != GameState.IN_PROGRESS:
            return 0

        material_advantage = (game.white.score - game.black.score)*100
        mobility = len(game.validMoves)
        isChecked = 30 if game.board.is_checked(game.turn) else 0

        score = (material_advantage + mobility - isChecked 
                 if game.turn == PieceColor.WHITE 
                 else material_advantage - mobility + isChecked)

        return score    
