import os, re, json 
import numpy as np
from dotenv import load_dotenv
from functools import reduce

from src.piece import Piece, PieceType, Move, MoveType, Queen, Rook, King, Knight, Bishop, Pawn, PieceColor, PieceState
from src.chessgame import ChessGame, GameSnapshot, GameState
from src.chessboard import ChessBoard

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
    
    p_str = piece.type.value if piece.type not in (PieceType.LIGHT_BISHOP,PieceType.DARK_BISHOP) else "B"

    return p_str.lower() if piece.color == PieceColor.BLACK else p_str

def gen_castle_str(board: np.array, k_i: int, k_j: int, r_i: int, r_j: int) -> str:
    """
    Helper function to help build the castling rights string.
    
    Receives the board and the coords where the king and the rook must be in order to castle.
    Return a non-empty string if castling is available, whether it may not be a legal move
    """
    side = "k" if r_j == 7 else "q"

    if (board[r_i][r_j] and board[r_i][r_j].type == PieceType.ROOK and board[r_i][r_j].state == PieceState.NOT_MOVED and
        board[k_i][k_j] and board[k_i][k_j].type == PieceType.KING and board[k_i][k_j].state == PieceState.NOT_MOVED):
        return side if k_i == 0 else side.upper() 
    
    return ""

def chessgame_to_fen(game: ChessGame) -> str:
    """
    Generate the fen string of the given ChessGame.
    """
    board = game.board.board

    board_str = "/".join([reduce((lambda x, y: x+y),map(piece_to_str,board[i])) for i in range(8)])
    board_str = re.sub(r' +', lambda m: str(len(m.group(0))), board_str)

    active_color = 'w' if game.turn == PieceColor.WHITE else 'b'

    castling_rights = "".join([gen_castle_str(board,*coords) for coords in [(7,4,7,7),
                                                                            (7,4,7,0),
                                                                            (0,4,0,7),
                                                                            (0,4,0,0)]])

    if castling_rights == "":
        castling_rights = "-"

    # enpassant_capture = next((move for move in game.validMoves if move.type == MoveType.ENPASSANT),None)
    # enpassant_str = numCoord_to_chessCoord(*enpassant_capture.coords[2:]) if enpassant_capture else '-'

    lastMove = game.stateHistory[-1].lastMove

    enpassant_str = '-'

    # Checks if the last move was a two square pawn advance
    if (lastMove and lastMove.type == MoveType.NORMAL):
        piece = board[lastMove.coords[2]][lastMove.coords[3]]
        if (piece.type == PieceType.PAWN and piece.color != game.turn and abs(piece.initial_row-lastMove.coords[2]) == 2):
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
            np_board[i][j].state = PieceState.MOVED
            j += 1    
        # Go to the next rank
        elif c == '/':
            i+=1
            j=0

    moveName_to_Move = {
        "-": None, 
        "a3": Move((6,0,4,0),MoveType.NORMAL),
        "b3": Move((6,1,4,1),MoveType.NORMAL),
        "c3": Move((6,2,4,2),MoveType.NORMAL),
        "d3": Move((6,3,4,3),MoveType.NORMAL),
        "e3": Move((6,4,4,4),MoveType.NORMAL),
        "f3": Move((6,5,4,5),MoveType.NORMAL),
        "g3": Move((6,6,4,6),MoveType.NORMAL),
        "h3": Move((6,7,4,7),MoveType.NORMAL),
        "a6": Move((1,0,3,0),MoveType.NORMAL),
        "b6": Move((1,1,3,1),MoveType.NORMAL),
        "c6": Move((1,2,3,2),MoveType.NORMAL),
        "d6": Move((1,3,3,3),MoveType.NORMAL),
        "e6": Move((1,4,3,4),MoveType.NORMAL),
        "f6": Move((1,5,3,5),MoveType.NORMAL),
        "g6": Move((1,6,3,6),MoveType.NORMAL),
        "h6": Move((1,7,3,7),MoveType.NORMAL),
    }

    lastMove = moveName_to_Move[enpassant_square]

    turn = PieceColor.WHITE if active_color == 'w' else PieceColor.BLACK 
    

    # Setting the state of the Rooks and the King based on castling rights
    if('Q' in castling):
        np_board[7][0].state = PieceState.NOT_MOVED
        np_board[7][4].state = PieceState.NOT_MOVED
    
    if('K' in castling):
        np_board[7][7].state = PieceState.NOT_MOVED
        np_board[7][4].state = PieceState.NOT_MOVED
    
    if('q' in castling):
        np_board[0][0].state = PieceState.NOT_MOVED
        np_board[0][4].state = PieceState.NOT_MOVED
    
    if('k' in castling):
        np_board[0][7].state = PieceState.NOT_MOVED
        np_board[0][4].state = PieceState.NOT_MOVED

    game = ChessGame()
    game.board = ChessBoard(customBoard=np_board)
    game.turn = turn
    game.validMoves = game.board.gen_valid_moves(game.turn,lastMove)
    game.stateHistory = [GameSnapshot(validMoves=game.validMoves,
                                      state=GameState.IN_PROGRESS,
                                      board=np_board.copy(),
                                      deadMoves=int(dead_moves),
                                      lastMove=lastMove)]
    game.white = None
    game.black = None
    game.deadMoves = int(dead_moves)
    game.totalMoves = int(total_moves)
    game.state = GameState.IN_PROGRESS

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

