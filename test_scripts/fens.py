import os, re, json 
import numpy as np
from dotenv import load_dotenv
from functools import reduce

from chess.piece import Piece, PieceType, Move, MoveType, Queen, Rook, King, Knight, Bishop, Pawn, PieceColor
from chess.chessgame import ChessGame, GameSnapshot, GameState
from chess.chessboard import ChessBoard

load_dotenv()
ROOT_DIR = os.getenv("ROOT_DIR")

letters = ['a','b','c','d','e','f','g','h']

piece_symbols = {
    PieceType.PAWN: "P",
    PieceType.KNIGHT: "N",
    PieceType.LIGHT_BISHOP: "B",
    PieceType.DARK_BISHOP: "B",
    PieceType.ROOK: "R",
    PieceType.QUEEN: "Q",
    PieceType.KING: "K"
}

def numCoord_to_chessCoord(x: int, y: int) -> str:
    return letters[y] + str(abs(x-8))

def moveObj_to_moveName(move: Move, all_moves: list[Move], board: np.ndarray) -> str:
    """
    Converts a Move Object into a string with the move name in Algebraic Notation.

    https://en.wikipedia.org/wiki/Algebraic_notation_(chess) -> link to move naming rules.
    """
    (x,y,x2,y2) = move.coords
    piece = board[x][y]
    
    if(move.type == MoveType.CASTLE):
        return "O-O" if y-y2 < 0 else "O-O-O"

    if piece.type == PieceType.PAWN:
        name = (("" if(move.type == MoveType.NORMAL or move.type == MoveType.PROMOTION_NORMAL) 
                    else letters[y] + 'x') 
                    + numCoord_to_chessCoord(x2,y2))
        if(move.type == MoveType.PROMOTION_CAPTURE or move.type == MoveType.PROMOTION_NORMAL):
            name = name + f'={piece_symbols[move.promotion]}'
        return name

    ls = [m.coords[:2] for m in all_moves 
            if board[m.coords[0]][m.coords[1]].type == piece.type  
               and (x,y) != m.coords[:2]  
               and (x2,y2) == m.coords[2:]]

    # Special case that can lead into ambiguous move names: Multiple pieces of the same type that can legally move to the same square
    if ls:
        # Case when we need to specify the current SQUARE of the piece to remove ambiguity
        if (next(((r,c) for (r,c) in ls if r == x),None) and 
            next(((r,c) for (r,c) in ls if c == y),None)):
            return (piece_symbols[piece.type] 
                    + numCoord_to_chessCoord(x,y) 
                    + ("" if move.type == MoveType.NORMAL else "x") 
                    + numCoord_to_chessCoord(x2,y2))

        # Case when we need to specify the current ROW of the piece to remove ambiguity
        if next(((r,c) for (r,c) in ls if y == c),None):
            return (piece_symbols[piece.type] 
                    + str(abs(x-8))  
                    + ("" if move.type == MoveType.NORMAL else "x") 
                    + numCoord_to_chessCoord(x2,y2))

        # Case when we need to specify the current COLUMN of the piece to remove ambiguity
        return (piece_symbols[piece.type] 
                + letters[y]
                + ("" if move.type == MoveType.NORMAL else "x") 
                + numCoord_to_chessCoord(x2,y2))

    return piece_symbols[piece.type] + ("" if move.type == MoveType.NORMAL else "x") + numCoord_to_chessCoord(x2,y2)

def piece_to_str(piece: Piece | None):
    """
    Helper function to help build the board string.
    """
    if not piece:
        return " "
    
    p_str = piece_symbols[piece.type]
    return p_str.lower() if piece.color == PieceColor.BLACK else p_str

def chessgame_to_fen(game: ChessGame) -> str:
    """
    Generate the fen string of the given ChessGame.
    """
    board = game.board.board

    board_str = "/".join([reduce((lambda x, y: x+y),map(piece_to_str,board[i])) for i in range(8)])
    board_str = re.sub(r' +', lambda m: str(len(m.group(0))), board_str)

    active_color = 'w' if game.turn == PieceColor.WHITE else 'b'

    castling_rights = "".join(["K" if game.WK else "", 
                               "Q" if game.WQ else "", 
                               "k" if game.BK else "", 
                               "q" if game.BQ else ""])

    if castling_rights == "":
        castling_rights = "-"

    lastMove = game.snapshots[-1].lastMove

    enpassant_str = '-'

    # Checks if the last move was a two square pawn advance
    if (lastMove and lastMove.type == MoveType.NORMAL):
        piece = board[lastMove.coords[2]][lastMove.coords[3]]
        if (piece.type == PieceType.PAWN 
            and piece.color != game.turn 
            and abs(piece.initial_row-lastMove.coords[2]) == 2
            and piece.initial_row == lastMove.coords[0]):
            
            aux = -1 if game.turn == PieceColor.WHITE else 1
            enpassant_str = numCoord_to_chessCoord(lastMove.coords[2]+aux,lastMove.coords[3]) 

    dead_moves_str = str(game.deadMoves)
    total_moves_str = str(game.totalMoves)

    return " ".join([board_str,active_color,castling_rights,enpassant_str,dead_moves_str,total_moves_str])

def fen_to_chessgame(fen: str) -> ChessGame:
    """
    Converts a FEN string into a ChessGame object.

    
    https://en.wikipedia.org/wiki/Forsyth%E2%80%93Edwards_Notation -> info about FEN notation.
    
    Some attributes such as StateHistory are not possible to get once fen strings do not 
    carry info about the previous moves played in the game, thereby some attributes of the 
    generated ChessGame object are set to None. 
    """
    np_board = np.full((8, 8), None, dtype=object)
    
    piece_placement, active_color, castling, enpassant_square, dead_moves, total_moves = fen.split()[:6]
    
    dict_piece = {
            'P': Pawn,
            'R': Rook,
            'N': Knight,
            'B': Bishop,
            'Q': Queen,
            'K': King
        }
        
    i = j = 0
    
    for c in piece_placement:
        # Skips c squares
        if(c.isdigit()):
            j += int(c)
        # Put a piece in the i,j square
        elif c.isalpha():
            np_board[i][j] = dict_piece[c.upper()](PieceColor.WHITE if c.isupper() else PieceColor.BLACK,(i,j)) 
            j += 1    
        # Go to the next rank
        elif c == '/':
            i+=1
            j=0

    moveName_to_Coord = {
        "-": None, 
        "a3": (4,0),
        "b3": (4,1),
        "c3": (4,2),
        "d3": (4,3),
        "e3": (4,4),
        "f3": (4,5),
        "g3": (4,6),
        "h3": (4,7),
        "a6": (3,0),
        "b6": (3,1),
        "c6": (3,2),
        "d6": (3,3),
        "e6": (3,4),
        "f6": (3,5),
        "g6": (3,6),
        "h6": (3,7),
    }

    enpassant_coord = moveName_to_Coord[enpassant_square]

    turn = PieceColor.WHITE if active_color == 'w' else PieceColor.BLACK 
    
    game = ChessGame()
    game.turn = turn
    
    game.WQ = ('Q' in castling)
    game.WK = ('K' in castling)
    game.BQ = ('q' in castling)
    game.BK = ('k' in castling)
        
    castling_bools = (game.BK,game.BQ) if game.turn == PieceColor.BLACK else (game.WK,game.WQ)
    
    pieces = [piece for piece in np_board.flat if piece and piece.color == turn]
    oppsPieces = [piece for piece in np_board.flat if piece and piece.color != turn]

    game.white.piecesLeft = [piece for piece in np_board.flat if piece and piece.color == PieceColor.WHITE]
    game.black.piecesLeft = [piece for piece in np_board.flat if piece and piece.color == PieceColor.BLACK]

    game.board = ChessBoard(customBoard=np_board)
    game.validMoves = game.board.gen_valid_moves(game.turn,pieces,oppsPieces,*castling_bools,enpassant_coord)
    game.snapshots = [GameSnapshot(validMoves=game.validMoves,
                                      state=GameState.IN_PROGRESS,
                                      deadMoves=int(dead_moves),
                                      WK=game.WK,
                                      WQ=game.WQ,
                                      BK=game.BK,
                                      BQ=game.BQ,
                                      lastMove=None)]
    
    game.deadMoves = int(dead_moves)
    game.totalMoves = int(total_moves)
    game.state = GameState.IN_PROGRESS
    game.init_zobrist()

    return game    

if __name__ == "__main__":
    
    testcases = ['famous',
             'pawns',
             'stalemates',
             'standard',
             'taxing',
             'checkmates',
             'promotions',
             'castling']

    for name in testcases:
        with open(f'{ROOT_DIR}/test_scripts/testcases/{name}.json','r') as file:
            data_dict = json.load(file)

        for test in data_dict["testCases"]:

            fen = test["start"]["fen"]    
            game = fen_to_chessgame(fen)
            fen2 = chessgame_to_fen(game)

            if (fen!=fen2):
                print("test failed")
                print(fen)
                print(fen2)
                print()
                


