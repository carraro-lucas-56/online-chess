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
        self.rect = Rect((180 + 80*c,130 + 80*r),square_size)


def coord_to_piece(col: int, x: int, y: int, turn: PieceColor) -> PieceType | None:
    """
    (x,y) are the coords selected by the user.
    col is the columns where the promotion will occur.
    This function detects which piece the user wants to promote his pawn to.
    For example, if there's a white pawn is on (0,5), the promotion options 
    will be displayed in (0,5),(1,5),(2,5),(3,5), if the user doesn't select
    any of those coords, return None.
    """
    if col != y:
        return None 
    
    (row,aux) = (0,1) if turn == PieceColor.WHITE else (7,-1) 

    if x == row:
        return PieceType.QUEEN
    elif x == row+aux:
        return PieceType.ROOK
    elif x == row+2*aux: 
        return PieceType.LIGHT_BISHOP if is_light_square((row,col)) else PieceType.DARK_BISHOP
    elif x == row+3*aux:
        return PieceType.KNIGHT

    return None

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
SCREEN_HEIGHT = 900
SQUARE_SIZE = 80

#Create a white screen 
DISPLAYSURF = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
pygame.display.set_caption("chess board")


game = ChessGame()
game.start_game()

squares = [[Rect((x,y),(SQUARE_SIZE,SQUARE_SIZE)) for x in range(180,180+(8*SQUARE_SIZE)+1,SQUARE_SIZE)] 
                                                  for y in range(130,130+(8*SQUARE_SIZE)+1,SQUARE_SIZE)]

pieces = [PieceImage(piece,(SQUARE_SIZE,SQUARE_SIZE)) for piece in game.board.board.flat if piece]

r = c = r2 = c2 = None

# Variable to detect if a promotion is happening
prom = False 

# Variable to save which piece the user wants to promote to
prom_piece = None 

# Images to display the pieces that the user can promote to
prom_pieces_images = None

running = True

while running:
    DISPLAYSURF.fill(BLACK)

    # Draws the board
    for x in range(8):
        for y in range(8):
            # Highlight selected square, if any
            if (None not in (r,c)) and r == x and c == y:
                pygame.draw.rect(DISPLAYSURF,
                                 RED,
                                 squares[x][y])
            else:
                pygame.draw.rect(DISPLAYSURF,
                                 WHITE if (x+y) % 2 == 0 else GREEN,
                                 squares[x][y])

    # Draw the pieces 
    for piece in pieces:
        DISPLAYSURF.blit(piece.image,piece.rect)

    # Draw promotion 'animation' if there's a promotion happening
    if prom:
        aux = -1 if game.turn == PieceColor.BLACK else 1

        for i in range(4):
            pygame.draw.rect(DISPLAYSURF,
                             WHITE,
                             Rect((180 + 80*c2,130 + 80*(r2+aux*i)),(SQUARE_SIZE,SQUARE_SIZE)))

        if not prom_pieces_images:
            prom_pieces_images = [PieceImage(p_type(game.turn,(r2+aux*i,c2)),(SQUARE_SIZE,SQUARE_SIZE)) for (p_type,i) in zip([Queen,Rook,Bishop,Knight],range(4))]

        for piece in prom_pieces_images:
            DISPLAYSURF.blit(piece.image,piece.rect)

    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
         
        # Get user's click coords 
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            x, y = event.pos
            col = (x - 180) // SQUARE_SIZE
            row = (y - 130) // SQUARE_SIZE

            # Checks if a square was clicked 
            if 0 <= row < 8 and 0 <= col < 8:
                # If a promotion is happening, checks if the user select a piece to promote to 
                if prom and not prom_piece:
                    prom_piece = coord_to_piece(c2,row,col,game.turn)
                elif None not in (r,c):
                    r2 = row
                    c2 = col
                else:
                    r = row
                    c = col

    # Applies selected move
    if None not in (r, c, r2, c2):
        # Checks if the user is trying to perform a valid promotion.
        if not prom and game.can_toggle_promotion(r,c,r2,c2):
            prom = True
        # This next if clause will trigger in two cases:
        # -> The user is trying to perform a non-promotion move.
        # -> The user is trying to perfrom a promotion and already selected a piece to promote to. 
        elif not prom or prom_piece:
            try:
                game.play_move(r,c,r2,c2,prom_piece)            
                pieces = [PieceImage(piece,(SQUARE_SIZE,SQUARE_SIZE)) for piece in game.board.board.flat if piece]
            except GameNotInProgress:
                pass
            except InvalidMove:
                pass
            if prom:
                prom = False
                prom_piece = None
                prom_pieces_images = None 
            r = c = r2 = c2 = None

    pygame.display.update()
    FramePerSec.tick(FPS)
