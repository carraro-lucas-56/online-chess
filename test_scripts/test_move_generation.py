from test_scripts.fens import fen_to_chessgame, moveObj_to_moveName

import os, json
from dotenv import load_dotenv

load_dotenv()
ROOT_DIR = os.getenv("ROOT_DIR")


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

Testcases can be found here -> https://github.com/schnitzi/rampart/blob/master
"""

def run_testcase(file_path):

    with open(file_path,'r') as file:
        data_dict = json.load(file)

    for i, test in enumerate(data_dict["testCases"]):
        fen = test["start"]["fen"]
        game = fen_to_chessgame(fen)
        board, move_objs = game.board, game.validMoves

        # Moves that deliveries a check (i.e moves that end wiht '+' ) have the '+' character removed
        expected = [item["move"] if (item["move"][-1] != '+' and item["move"][-1] != '#') else item["move"][:-1] for item in test["expected"]]

        actual = [moveObj_to_moveName(move,move_objs,board.board) for move in move_objs]

        if set(actual) == set(expected):
            pass
            # print(f"test {i+1} passed")
        else:
            print(f"test {i} failed ")
            print(fen)
            board.print_board()
            print(f"expeceted: {expected}")
            print(f"actual:    {actual}")
            print()

testcases = ['famous',
             'pawns',
             'stalemates',
             'standard',
             'taxing',
             'checkmates',
             'promotions',
             'castling']

if __name__=="__main__":
    for i, test in enumerate(testcases):
        print(50*'-')
        print(f'Testcase {i+1} -> {test}.json')
        print(50*'-')
        run_testcase(f'{ROOT_DIR}/test_scripts/testcases/{test}.json')
    