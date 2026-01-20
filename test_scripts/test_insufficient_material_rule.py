from test_scripts.Utils import *
from src.chessgame import ChessGame

# Chess positions where checkmate is impossible even with cooperation.
fens = [
    "8/8/8/8/8/8/8/Kk6 w - - 0 1",
    "8/8/8/8/8/8/8/KBk5 w - - 0 1",
    "8/8/8/8/8/8/8/KNk5 w - - 0 1",
    "8/8/8/8/8/8/2B5/KBk5 w - - 0 1",
    "8/8/8/8/8/8/1n6/KNk5 w - - 0 1",
    "8/8/8/8/8/8/1n6/KBk5 w - - 0 1",
    "8/8/8/8/8/8/1b1b4/Kk6 w - - 0 1",
    "8/8/8/8/8/8/1b1b1b1b/Kk6 w - - 0 1",
    "8/8/8/8/8/8/1bN5/Kk6 w - - 0 1"
]

for fen in fens:
    game = ChessGame()

    board, _ = fen_to_chessboard(fen)

    game.board = board 
    game.white.piecesLeft = [p.type for p in board.board.flat if p and p.color == PieceColor.WHITE]
    game.black.piecesLeft = [p.type for p in board.board.flat if p and p.color == PieceColor.BLACK]
    game.validMoves = game.board.gen_valid_moves(PieceColor.WHITE)
    # print(fen)
    # game.board.print_board()

    game._update_state()
    print(game.state.name)
    