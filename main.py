import pygame, sys
from pygame.locals import *
from src.chessgame import *
from dotenv import load_dotenv
import os 

load_dotenv()
ROOT_DIR = os.getenv("ROOT_DIR")

class PieceImage:
    def __init__(self, piece: Piece, square_size: tuple[int,int]):
        (r,c) = piece.position
        name = piece.type.name.lower() if piece.type != PieceType.LIGHT_BISHOP and piece.type != PieceType.DARK_BISHOP else "bishop"
        image = pygame.image.load(f'{ROOT_DIR}/images/{piece.color.name.lower()}-{name}.png')
        
        self.image = pygame.transform.scale(image,square_size)
        self.rect = Rect((100 + 80*c,100 + 80*r),square_size)

#Initializing 
pygame.init()
 
#Setting up FPS 
FPS = 40
FramePerSec = pygame.time.Clock()

WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255,0,0)
BLACK = (0, 0, 0)

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 1000

#Create a white screen 
DISPLAYSURF = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
pygame.display.set_caption("chess board")

running = True

SQUARE_SIZE = (80,80)

squares = [[Rect((x,y),SQUARE_SIZE) for x in range(100,661,80)] for y in range(100,661,80)]

# pawn_image = pygame.image.load('/home/lucas-carraro/Documents/chess_game/images/white_pawn.svg')
# pawn_image = pygame.transform.scale(pawn_image, SQUARE_SIZE)

game = ChessGame()
game.start_game()

pieces = [PieceImage(piece,SQUARE_SIZE) for piece in game.board.board.flat if piece]

r = c = r2 = c2 = None

while running:
    DISPLAYSURF.fill(BLACK)

    for x in range(8):
        for y in range(8):
            if (None not in (r,c)) and r == x and c == y:
                pygame.draw.rect(DISPLAYSURF,
                                 RED,
                                 squares[x][y])
            else:
                pygame.draw.rect(DISPLAYSURF,
                                 WHITE if (x+y) % 2 == 0 else GREEN,
                                 squares[x][y])
                
    for piece in pieces:
        DISPLAYSURF.blit(piece.image,piece.rect)

    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            x, y = event.pos
            col = (x - 100) // 80
            row = (y - 100) // 80

            if 0 <= row < 8 and 0 <= col < 8:
                if None not in (r,c):
                    r2 = row
                    c2 = col
                else:
                    r = row
                    c = col

    if None not in (r, c, r2, c2):
        try:
            game.play_move(r,c,r2,c2)
            pieces = [PieceImage(piece,SQUARE_SIZE) for piece in game.board.board.flat if piece]
        except GameNotInProgress:
            pass
        except InvalidMove:
            pass
        r = c = r2 = c2 = None

    pygame.display.update()
    FramePerSec.tick(FPS)
