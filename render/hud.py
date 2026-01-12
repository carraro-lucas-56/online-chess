import pygame
from src.chessgame import ChessGame, PieceColor
from render.board_view import PieceImage

WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255,0,0)
BLACK = (0, 0, 0)

class ClockView:
    def __init__(self, pos):
        self.font = pygame.font.Font(None, 36)
        self.pos = pos

    def draw(self, surface, seconds: float):
        minutes = int(seconds) // 60
        secs = int(seconds) % 60
        text = f"{minutes:02}:{secs:02}"

        img = self.font.render(text, True, WHITE)
        surface.blit(img, self.pos)

class ScoreView():
    def __init__(self,pos_white,pos_black):
        self.pos_white = pos_white
        self.pos_black = pos_black
        self.font = pygame.font.Font(None, 36)
    
    def draw(self, surface: pygame.Surface, white_score: int, black_score: int) -> None:
        if(white_score > black_score):
            img = self.font.render(f'+{white_score-black_score}', True, WHITE)
            surface.blit(img, self.pos_white)
        elif(white_score < black_score):
            img = self.font.render(f'+{black_score-white_score}', True, WHITE)
            surface.blit(img, self.pos_black)

class Hud:
    def __init__(self, game: ChessGame, square_size: int):
        self.square_size = square_size
        self.black_clock = ClockView((180, 90))
        self.white_clock = ClockView((180, 130 + 8*square_size+ 20))
        self.score = ScoreView(pos_white=(180+7.5*self.square_size,130+8*self.square_size+20),
                               pos_black=(180+7.5*self.square_size,90))
        self.white_pieces_capt = []
        self.black_pieces_capt = []
        self.game = game

    def draw(self, surface: pygame.Surface) -> None:
        self.white_clock.draw(surface, self.game.white.time_left)
        self.black_clock.draw(surface, self.game.black.time_left)
        
        self.score.draw(surface,
                        white_score=self.game.white.score,
                        black_score=self.game.black.score)
        
        if len(self.white_pieces_capt) < len(self.game.white.piecesCaptured):
            x = len(self.white_pieces_capt)
            p_type = self.game.white.piecesCaptured[-1]
            self.white_pieces_capt.append(PieceImage(pos=(400+20*x,130+8*self.square_size+20),
                                                     square_size=(30,30),
                                                     p_type=p_type,
                                                     p_color=PieceColor.BLACK))

        if len(self.black_pieces_capt) < len(self.game.black.piecesCaptured):
            x = len(self.black_pieces_capt)
            p_type = self.game.black.piecesCaptured[-1]
            self.black_pieces_capt.append(PieceImage(pos=(400+20*x,90),
                                                     square_size=(30,30),
                                                     p_type=p_type,
                                                     p_color=PieceColor.WHITE))
        
        for piece in self.black_pieces_capt:
            piece.draw(surface)
        for piece in self.white_pieces_capt:
            piece.draw(surface)
            