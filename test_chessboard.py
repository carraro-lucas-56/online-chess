from chessboard import *
import json
import os
from dotenv import load_dotenv

load_dotenv()
ROOT_DIR = os.getenv("ROOT_DIR")

"""
IMPORTANT: we're assuming that if any king or rook are in it's original square, so it wasn't moved.
That's a necessary condition to generate available castling moves because fen strings do not move history.
So we can't check if the rook/king have already moved.
"""


letters = ['a','b','c','d','e','f','g','h']

def numCoord_to_chessCoord(x: int, y: int) -> str:
    return letters[y] + str(abs(x-8))

def moveObj_to_moveName(move: Move, all_moves: list[Move], board: np.ndarray) -> str:
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
        return "O-O" if y-y2 < 2 else "O-O-O"

    # Special case that can lead into ambiguous move names: Two Rooks/Knights that can move to the same square
    if((type(piece) == Rook or type(piece) == Knight) and 
       any(type(board[m.coords[0]][m.coords[1]]) == type(piece) and (x,y) != m.coords[:2] and (x2,y2) == m.coords[2:] for m in all_moves)):

        # Both are in the same column, must add row indication before the destination square
        if any (row != x and board[row][y] and type(board[row][y]) == type(Piece) and board[row][y].color == piece.color for row in range(8)):
            return dict_piece[type(Piece)] + str(abs(x-8)) + + ("" if move.type == MoveType.NORMAL else "x") + numCoord_to_chessCoord(x2,y2)

        # Otherwise must add column indication before the destination square
        return dict_piece[type(piece)] + letters[y] + ("" if move.type == MoveType.NORMAL else "x") + numCoord_to_chessCoord(x2,y2)

    if type(piece) == Pawn:
        return ("" if(move.type == MoveType.NORMAL) else letters[y] + 'x') + numCoord_to_chessCoord(x2,y2)

    return dict_piece[type(piece)] + ("" if move.type == MoveType.NORMAL else "x") + numCoord_to_chessCoord(x2,y2)

def fen_to_chessboard(fen: str) -> tuple[ChessBoard,list[Move]]:
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
            j += 1    
        # Go to the next rank
        elif c == '/':
            i+=1
            j=0

    turn = PieceColor.WHITE if active_color == 'w' else PieceColor.BLACK 

    moveName_to_moveCoords = {
        "-": (1,1,1,1), # just a random ivalid move 
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
    board = ChessBoard(np_board)

    return board, board.gen_valid_moves(turn,lastMove)

def run_testcase(file_path):

    with open(file_path,'r') as file:
        data_dict = json.load(file)

    for i, test in enumerate(data_dict["testCases"]):
        fen = test["start"]["fen"]
        board, move_objs = fen_to_chessboard(fen)

        # Moves that deliveries a check (i.e moves that end wiht '+' ) have the '+' character removed
        expected = [item["move"] if item["move"][-1] != '+' else item["move"][:-1] for item in test["expected"]]

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

testcases = ['famous','pawns','stalemates','standard']

for i, test in enumerate(testcases):
    print(50*'-')
    print(f'Testcase {i+1}')
    print(50*'-')
    run_testcase(f'{ROOT_DIR}/testcases/{test}.json')