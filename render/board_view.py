import pygame 
from pygame.locals import *
from src.chessgame import *
from assets import ImageCache

WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255,0,0)
BLACK = (0, 0, 0)

class PieceImage:
    def __init__(self, piece: Piece, square_size: tuple[int, int]):
        r, c = piece.position
        p_name = "bishop" if piece.type in (
            PieceType.LIGHT_BISHOP, PieceType.DARK_BISHOP
        ) else piece.type.name.lower()
        name = f"{piece.color.name.lower()}-{p_name}"

        self.image = ImageCache.get(name, square_size)
        self.rect = Rect((180 + 80*c, 130 + 80*r), square_size)

    def draw(self, surface):
        surface.blit(self.image, self.rect)

    def update_position(self,r: int, c: int, square_size):
        self.rect = Rect((180 + 80*c,130 + 80*r),square_size)

class InvalidPromotionSquare(Exception):
    pass

class BoardImage:
    def __init__(self, game: ChessGame, square_size: tuple[int,int]):
        self.squares =  [[Rect((x,y),square_size) for x in range(180,180+(8*square_size[0])+1,square_size[0])] 
                                                  for y in range(130,130+(8*square_size[0])+1,square_size[0])]

        self.square_size = square_size
        self.pieces = [PieceImage(piece,square_size) for piece in game.board.board.flat if piece]
        self.prom_pieces = [PieceImage(p_type(game.turn,(0+i,0)),square_size) 
                                       for (p_type,i) in zip([Queen,Rook,Bishop,Knight],range(4))]

    def draw_prom_pieces(self, surface: pygame.Surface, r: int, c: int):
        """
        Receives the square coords where a promotion is happening 
        and display the pieces that the player can promote to.
        """
        if r != 0 and r != 7:
            raise InvalidPromotionSquare

        aux = -1 if r == 7 else 1

        for i in range(4):
            pygame.draw.rect(surface,
                             WHITE,
                             Rect((180 + 80*c,130 + 80*(r+aux*i)),self.square_size))

        for i, piece in enumerate(self.prom_pieces):
            piece.update_position(r+aux*i,c,self.square_size)
            piece.draw(surface)

    def draw(self, surface: pygame.Surface, highlighted_squares: tuple[int,int] | None = None):
        # Draw the squares
        for x in range(8):
            for y in range(8):
                # Highlight selected square, if any
                if (x,y) == highlighted_squares:
                    pygame.draw.rect(surface,
                                     RED,
                                     self.squares[x][y])
                else:
                    pygame.draw.rect(surface,
                                     WHITE if (x+y) % 2 == 0 else GREEN,
                                     self.squares[x][y])

        # Draw the pieces 
        for piece in self.pieces:
            piece.draw(surface)


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
