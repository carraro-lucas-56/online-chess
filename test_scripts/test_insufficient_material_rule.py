from test_scripts.fens import fen_to_chessgame
from src.piece import PieceColor

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
    game = fen_to_chessgame(fen)

    game.white.piecesLeft = [p.type for p in game.board.board.flat if p and p.color == PieceColor.WHITE]
    game.black.piecesLeft = [p.type for p in game.board.board.flat if p and p.color == PieceColor.BLACK]

    game._update_state()
    print(game.state.name)
    