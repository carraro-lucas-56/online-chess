from chessboard import *
from piece import *

class ChessGame():
    def __init__(self):
        self.turn = PieceColor.WHITE
        self.board = ChessBoard()
        self.inProgess = False 
        self.validMoves = [] # list with all the valid moves current available for the colos who's playing in this turn 

    def _change_turn(self) -> None:
        self.turn = PieceColor.WHITE if self.turn == PieceColor.BLACK else PieceColor.BLACK

    def _game_ended(self) -> bool:
        return not self.validMoves

    def play(self):
        """
        Function that runs the game loop
        """
        self.inProgress = True  
        self.validMoves = self.board.gen_valid_moves(self.turn)

        # main game loop
        while(self.inProgress):
            print(self.validMoves)
            self.board.print_board()
        
            # read user move
            x = int(input())
            y = int(input())
            x2 = int(input())
            y2 = int(input())

            # Asks for another move ultil we get a valid one
            while not any((x,y,x2,y2) == move.coords for move in self.validMoves):            
                x = int(input())
                y = int(input())
                x2 = int(input())
                y2 = int(input())

            moves = [m for m in self.validMoves if m.coords == (x,y,x2,y2)]
            
            # Checking for promotions
            if(len(moves) > 1):
                prom_piece = input()
                move = next(m for m in moves if m.promotion.value == prom_piece)
            else:
                move = moves[0]

            # apply the move and checks if the game ended
            self.board._apply_move(move)
            self._change_turn()
            self.validMoves = self.board.gen_valid_moves(self.turn,move)

            if self._game_ended():
                self.inProgress = False

            print(self.turn.name)

game = ChessGame()
game.play()
