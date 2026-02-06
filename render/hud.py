import pygame

from chess.piece import PieceColor, Piece
from chess.chessgame import ChessGame, GameState
from render.board_view import PieceImage
from render.colors import WHITE, BLACK

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

class PiecesCapturedView():
    def __init__(self, squre_size: tuple[int,int], pos: tuple[int,int], p_color: PieceColor):
        self.square_size = squre_size
        self.pieces = []
        self.pos = pos # Position of the first piece to be drawn
        self.color = p_color

    def draw(self, surface: pygame.Surface, ps_captured: list[Piece]):
        if len(self.pieces) < len(ps_captured):
            x = len(self.pieces)
            p_type = ps_captured[-1].type
            self.pieces.append(PieceImage(pos=(self.pos[0]+x*20,self.pos[1]),
                                          square_size=(30,30),
                                          p_type=p_type,
                                          p_color=self.color))

        elif len(self.pieces) > len(ps_captured):
            self.pieces.pop()

        for piece in self.pieces:
            piece.draw(surface)

class Hud:
    def __init__(self, game: ChessGame, perspective: PieceColor ,square_size: int):
        self.square_size = square_size
        self.perspective = perspective

        if perspective == PieceColor.WHITE:
            self.black_clock = ClockView((180, 90))
            self.white_clock = ClockView((180, 130 + 8*square_size+ 20))
            self.score = ScoreView(pos_white=(180+7.5*self.square_size,130+8*self.square_size+20),
                                   pos_black=(180+7.5*self.square_size,90))
            self.white_pieces_capt = PiecesCapturedView(pos=(400,130+8*self.square_size+20),
                                                        p_color=PieceColor.BLACK,
                                                        squre_size=(30,30))
            self.black_pieces_capt = PiecesCapturedView(pos=(400,90),
                                                        p_color=PieceColor.WHITE,
                                                        squre_size=(30,30))
        else:   
            self.white_clock = ClockView((180, 90))
            self.black_clock = ClockView((180, 130 + 8*square_size+ 20))
            self.score = ScoreView(pos_black=(180+7.5*self.square_size,130+8*self.square_size+20),
                                   pos_white=(180+7.5*self.square_size,90))
            self.black_pieces_capt = PiecesCapturedView(pos=(400,130+8*self.square_size+20),
                                                        p_color=PieceColor.WHITE,
                                                        squre_size=(30,30))
            self.white_pieces_capt = PiecesCapturedView(pos=(400,90),
                                                        p_color=PieceColor.BLACK,
                                                        squre_size=(30,30))

        self.game = game

    def draw(self, surface: pygame.Surface) -> None:
        self.white_clock.draw(surface, self.game.white.time_left)
        self.black_clock.draw(surface, self.game.black.time_left)
        
        self.score.draw(surface,
                        white_score=self.game.white.score,
                        black_score=self.game.black.score)
        
        self.white_pieces_capt.draw(surface,self.game.white.piecesCaptured)
        self.black_pieces_capt.draw(surface,self.game.black.piecesCaptured)

        font = pygame.font.Font(None, 40)
        text = "Press q to quit"

        img = font.render(text, True, BLACK)
        surface.blit(img, (700,50))
            
        # Draws game result (if the game is finished)
        if self.game.state != GameState.IN_PROGRESS:
            match self.game.state:
                case GameState.CHACKMATE:
                    result = "lost" if self.game.turn == self.perspective else "won"
                    text = f"You {result} by Checkmate"
                case GameState.TIMEOUT:
                    result = "lost" if self.game.turn != self.perspective else "won"
                    text = f"You {result} on time"
                case _:
                    text = f"Draw by {self.game.state.name}"

            font = pygame.font.Font(None, 40)

            img = font.render(text, True, BLACK)
            surface.blit(img, (350,840))
            