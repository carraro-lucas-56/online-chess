import pygame 
from pygame.locals import *

from utils.utils import is_light_square
from src.chessgame import ChessGame
from src.piece import Piece, PieceType, PieceColor, Move
from assets import ImageCache
from render.colors import WHITE, RED, GREEN, BRIGHT_YELLOW, CANARY_YELLOW

class PieceImage:
    def __init__(self, pos, p_type, p_color, square_size):
        self.rect = Rect(pos,square_size)
        p_name = "bishop" if p_type in (
            PieceType.LIGHT_BISHOP, PieceType.DARK_BISHOP
        ) else p_type.name.lower()
        name = f"{p_color.name.lower()}-{p_name}"

        self.image = ImageCache.get(name, square_size)

    @classmethod
    def from_piece_obj(cls, piece: Piece, square_size: tuple[int, int]):
        r,c = piece.position
        return cls((180 + 80*c, 130 + 80*r),piece.type,piece.color,square_size)

    def draw(self, surface: pygame.Surface):
        surface.blit(self.image, self.rect)

    def update_position(self,r: int, c: int, square_size):
        self.rect = Rect((180 + 80*c,130 + 80*r),square_size)

class BoardImage:
    def __init__(self, game: ChessGame, square_size: tuple[int,int]):
        self.squares =  [[Rect((x,y),square_size) for x in range(180,180+(8*square_size[0])+1,square_size[0])] 
                                                  for y in range(130,130+(8*square_size[0])+1,square_size[0])]

        self.square_size = square_size
        self.pieces = [PieceImage.from_piece_obj(piece,square_size) for piece in game.board.board.flat if piece]
        self.white_prom_pieces = [PieceImage((1,1),p_type,PieceColor.WHITE,square_size) 
                             for p_type in [PieceType.QUEEN,PieceType.ROOK,PieceType.LIGHT_BISHOP,PieceType.KNIGHT]]
        self.black_prom_pieces = [PieceImage((1,1),p_type,PieceColor.BLACK,square_size) 
                             for p_type in [PieceType.QUEEN,PieceType.ROOK,PieceType.LIGHT_BISHOP,PieceType.KNIGHT]]


    def draw_prom_pieces(self, surface: pygame.Surface, r: int, c: int):
        """
        Receives the square coords where a promotion is happening 
        and display the pieces that the player can promote to.
        """
        if r != 0 and r != 7:
            return

        aux = -1 if r == 7 else 1

        for i in range(4):
            pygame.draw.rect(surface,
                             WHITE,
                             Rect((180 + 80*c,130 + 80*(r+aux*i)),self.square_size))

        for i, piece in enumerate(self.white_prom_pieces if r == 0 else self.black_prom_pieces):
            piece.update_position(r+aux*i,c,self.square_size)
            piece.draw(surface)

    def draw(self, surface: pygame.Surface, move: Move | None , selected_square: tuple[int,int] | None = None):
        if move: 
            (r,c) = move.coords[:2]
            (r2,c2) = move.coords[2:]

        # Draw the squares
        for x in range(8):
            for y in range(8):
                # Highlight selected square, if any
                if (x,y) == selected_square:
                    pygame.draw.rect(surface,
                                     RED,
                                     self.squares[x][y])
                elif move and ((x,y) == (r,c) or (x,y) == (r2,c2)):
                    pygame.draw.rect(surface,
                                     BRIGHT_YELLOW if not is_light_square((x,y)) else CANARY_YELLOW,
                                     self.squares[x][y])
                else:
                    pygame.draw.rect(surface,
                                     WHITE if (x+y) % 2 == 0 else GREEN,
                                     self.squares[x][y])

        # Draw the pieces 
        for piece in self.pieces:
            piece.draw(surface)

