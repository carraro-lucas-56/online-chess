from chessboard import *
import json
import os
from dotenv import load_dotenv

"""
This script is a test harness for validating chess move generation and
algebraic notation formatting against predefined test cases.

How the tests work:
1. Each test case provides a starting position encoded as a FEN string
   and a list of expected legal moves written in standard algebraic notation.
2. The FEN string is parsed into an internal ChessBoard representation,
   including piece placement, side to move, castling rights, and en passant.
3. All legal moves for the active player are generated from the board state.
4. Each generated Move object is converted into algebraic notation using
   moveObj_to_moveName, following standard chess notation rules.
5. Check ('+') and checkmate ('#') symbols are ignored when comparing results,
   since the focus is on move identity rather than check indication.
6. The set of generated move names is compared against the expected set.
   - If they match exactly, the test passes.
   - Otherwise, the board position, expected moves, and actual moves are printed
     to help diagnose the failure.

The goal of these tests is to ensure that move generation and move notation
are both correct and consistent with official chess rules.
"""


load_dotenv()
ROOT_DIR = os.getenv("ROOT_DIR")

letters = ['a','b','c','d','e','f','g','h']

def numCoord_to_chessCoord(x: int, y: int) -> str:
    return letters[y] + str(abs(x-8))

def moveObj_to_moveName(move: Move, all_moves: list[Move], board: np.ndarray) -> str:
    """
    Converts a Move Object into a string with the move name in Algebraic Notation.
    https://en.wikipedia.org/wiki/Algebraic_notation_(chess) -> link to move naming rules.
    """
    (x,y,x2,y2) = move.coords
    piece = board[x][y]

    dict_piece = {
            Pawn: 'P',
            Rook: 'R',
            Knight: 'N',
            Bishop: 'B',
            Queen: 'Q',
            King: 'K'
        }
    
    if(move.type == MoveType.CASTLE):
        return "O-O" if y-y2 < 0 else "O-O-O"

    if type(piece) == Pawn:
        name = (("" if(move.type == MoveType.NORMAL or move.type == MoveType.PROMOTION_NORMAL) 
                         else letters[y] + 'x') 
                    + numCoord_to_chessCoord(x2,y2))
        if(move.type == MoveType.PROMOTION_CAPTURE or move.type == MoveType.PROMOTION_NORMAL):
            name = name + f'={move.promotion.value}'
        return name

    ls = [m.coords[:2] for m in all_moves 
            if (type(board[m.coords[0]][m.coords[1]]) == type(piece)
                 and (x,y) != m.coords[:2] 
                 and (x2,y2) == m.coords[2:])]

    # Special case that can lead into ambiguous move names: Multiple pieces of the same type that can legally move to the same square
    if ls:
        # Case when we need to specify the current SQUARE of the piece to remove ambiguity
        if (next(((r,c) for (r,c) in ls if r == x),None) and 
            next(((r,c) for (r,c) in ls if c == y),None)):
            return (dict_piece[type(piece)] 
                    + numCoord_to_chessCoord(x,y) 
                    + ("" if move.type == MoveType.NORMAL else "x") 
                    + numCoord_to_chessCoord(x2,y2))

        # Case when we need to specify the current ROW of the piece to remove ambiguity
        if next(((r,c) for (r,c) in ls if y == c),None):
            return (dict_piece[type(piece)] 
                    + str(abs(x-8))  
                    + ("" if move.type == MoveType.NORMAL else "x") 
                    + numCoord_to_chessCoord(x2,y2))

        # Case when we need to specify the current COLUMN of the piece to remove ambiguity
        return (dict_piece[type(piece)] 
                + letters[y]
                + ("" if move.type == MoveType.NORMAL else "x") 
                + numCoord_to_chessCoord(x2,y2))

    return dict_piece[type(piece)] + ("" if move.type == MoveType.NORMAL else "x") + numCoord_to_chessCoord(x2,y2)

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

def run_testcase(file_path):

    with open(file_path,'r') as file:
        data_dict = json.load(file)

    for i, test in enumerate(data_dict["testCases"]):
        fen = test["start"]["fen"]
        board, move_objs = fen_to_chessboard(fen)

        # Moves that deliveries a check (i.e moves that end wiht '+' ) have the '+' character removed
        expected = [item["move"] if (item["move"][-1] != '+' and item["move"][-1] != '#') else item["move"][:-1] for item in test["expected"]]

        actual = [moveObj_to_moveName(move,move_objs,board.board) for move in move_objs]

        if set(actual) == set(expected):
            print(f"test {i+1} passed")
        else:
            print(f"test {i} failed ")
            print(fen)
            board.print_board()
            print(expected)
            print(actual)
            print()

testcases = ['famous','pawns','stalemates','standard','taxing','checkmates','promotions','castling']

for i, test in enumerate(testcases):
    print(50*'-')
    print(f'Testcase {i+1} -> {test}.json')
    print(50*'-')
    run_testcase(f'{ROOT_DIR}/testcases/{test}.json')
    