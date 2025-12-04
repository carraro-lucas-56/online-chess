from chessboard import *
from piece import *

class ChessGame():
    def __init__(self):
        self.turn = PieceColor.WHITE
        self.board = ChessBoard()
        self.inProgess = False 

    def _change_turn(self) -> None:
        self.turn = PieceColor.WHITE if self.turn == PieceColor.BLACK else PieceColor.WHITE

    def play(self):
        self.inProgress = True  

        while(self.inProgress):
            self.board.print_board()
            x = int(input())
            y = int(input())
            x2 = int(input())
            y2 = int(input())
            self.board._apply_move(x,y,x2,y2)

game = ChessGame()
game.play()

