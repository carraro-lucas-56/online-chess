from src.chessgame import *
from dotenv import load_dotenv
import os 

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

def fen_to_chessboard(fen: str) -> tuple[ChessBoard,list[Move]]:
    """
    Converts a FEN string into a ChessBoard object
    https://en.wikipedia.org/wiki/Forsyth%E2%80%93Edwards_Notation -> info about FEN notation
    """
    np_board = np.full((8, 8), None, dtype=object)
    
    piece_placement, active_color, castling, enpassant_square = fen.split()[:4]
    
    dict_piece = {
            'P': Pawn,
            'R': Rook,
            'N': Knight,
            'B': Bishop,
            'Q': Queen,
            'K': King
        }
        
    i = 0
    j = 0

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

    turn = PieceColor.WHITE if active_color == 'w' else PieceColor.BLACK 

    moveName_to_moveCoords = {
        "-": (1,1,1,1), 
        "a3": (6,0,4,0),
        "b3": (6,1,4,1),
        "c3": (6,2,4,2),
        "d3": (6,3,4,3),
        "e3": (6,4,4,4),
        "f3": (6,5,4,5),
        "g3": (6,6,4,6),
        "h3": (6,7,4,7),
        "a6": (1,0,3,0),
        "b6": (1,1,3,1),
        "c6": (1,2,3,2),
        "d6": (1,3,3,3),
        "e6": (1,4,3,4),
        "f6": (1,5,3,5),
        "g6": (1,6,3,6),
        "h6": (1,7,3,7),
    }

    lastMove = Move(moveName_to_moveCoords[enpassant_square],MoveType.NORMAL)

    (q,k,row) = ('Q','K',7) if turn == PieceColor.WHITE else ('q','k',0)  

    # Setting the state of the Rooks and the King based on castling rights
    if(q in castling):
        np_board[row][0].state = PieceState.NOT_MOVED
        np_board[row][4].state = PieceState.NOT_MOVED
    if(k in castling):
        np_board[row][7].state = PieceState.NOT_MOVED
        np_board[row][4].state = PieceState.NOT_MOVED
    
    board = ChessBoard(np_board)

    return board, board.gen_valid_moves(turn,lastMove)
