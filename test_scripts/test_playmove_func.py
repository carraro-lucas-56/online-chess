import json
import copy

from test_scripts.fens import fen_to_chessgame, moveObj_to_moveName, chessgame_to_fen, ROOT_DIR

def run_testcase(file_path):

    with open(file_path,'r') as file:
        data_dict = json.load(file)

    for i, test in enumerate(data_dict["testCases"]):
        fen = test["start"]["fen"]
        
        print(65*'-')
        print(f"FEN ({i+1}): {fen}")
        print(65*'-')

        game = fen_to_chessgame(fen)

        prev_np_board = copy.deepcopy(game.board.board)
        prev_valid_moves = game.validMoves

        move_to_fen = {(item["move"] 
                       if item["move"][-1] != '+' and item["move"][-1] != '#' 
                       else item["move"][:-1]) : item["fen"] 
                       for item in test["expected"]}

        for move in prev_valid_moves:
            
            game.play_move(*move.coords,move.promotion)
            move_name = moveObj_to_moveName(move,prev_valid_moves,prev_np_board)
            
            actual_fen = chessgame_to_fen(game)
            expected_fen = move_to_fen[move_name]            

            if(actual_fen != expected_fen):
                print(f"{move_name.ljust(5)} incorrect")
                print(f"Expected fen: {expected_fen}")
                print(f"Actual fen:   {actual_fen}",end="\n\n")
               
            game.unplay_move(pop=True)

            
testcases = ['standard',
             'castling',
             'checkmates',
             'famous',
             'pawns',
             'promotions',
             'stalemates',
             'taxing',
             ]

for i, test in enumerate(testcases):
    print(65*'=')
    print(f'Testcase {i+1} -> {test}.json')
    print(65*'=')
    run_testcase(f'{ROOT_DIR}/test_scripts/testcases/{test}.json')
    