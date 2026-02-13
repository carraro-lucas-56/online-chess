import os, json
from dotenv import load_dotenv

from .fens import fen_to_chessgame, moveObj_to_moveName

load_dotenv()
ROOT_DIR = os.getenv("ROOT_DIR")

def run_testcase(file_path: str) -> None:
    with open(file_path) as file:
        data_dict = json.load(file)

    for test in data_dict["testCases"]:
        fen = test["start"]["fen"]
        game = fen_to_chessgame(fen)
        original_hash = game.zobristHash

        for move in game.validMoves:
            game.play_move(move)
            game.unplay_move()    
            if(game.zobristHash != original_hash): 
                print("wrong")

testcases = ['standard',
             'castling',
             'checkmates',
             'famous',
             'pawns',
             'promotions',
             'stalemates',
             'taxing'
             ]

for i, test in enumerate(testcases):
        print(50*'-')
        print(f'Testcase {i+1} -> {test}.json')
        print(50*'-')
        run_testcase(f'{ROOT_DIR}/test_scripts/testcases/{test}.json')