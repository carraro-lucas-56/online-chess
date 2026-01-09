import pygame, sys
from assets import ImageCache
from pygame.locals import *
from src.chessgame import ChessGame
from dotenv import load_dotenv
from render.board_view import *
import os 

load_dotenv()
ROOT_DIR = os.getenv("ROOT_DIR")

def load_assets():
    for color in ("white", "black"):
        for piece in ("pawn", "rook", "knight", "bishop", "queen", "king"):
            name = f"{color}-{piece}"
            ImageCache.load(name, f"{ROOT_DIR}/images/{name}.png")


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

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 900
SQUARE_SIZE = 80

#Create a white screen 
DISPLAYSURF = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
pygame.display.set_caption("chess board")

clock = pygame.time.Clock()

black_clock = ClockView((180, 90))
white_clock = ClockView((180, 130 + 8*SQUARE_SIZE + 20))

load_assets()

game = ChessGame()
game.start_game()

boardImage = BoardImage(game, (SQUARE_SIZE,SQUARE_SIZE))

r = c = r2 = c2 = None

# Variable to detect if a promotion is happening
prom = False 

# Variable to save which piece the user wants to promote to
prom_piece = None 

running = True

while running:
    DISPLAYSURF.fill(BLACK)
    
    if game.state != GameState.IN_PROGRESS:
        text = game.state.name
        font = pygame.font.Font(None, 18)

        img = font.render(text, True, WHITE)
        DISPLAYSURF.blit(img, (180+8*SQUARE_SIZE+10,500))

    dt = clock.tick(FPS) / 1000  # seconds

    if game.turn == PieceColor.WHITE:
        game.white.time_left -= dt
    else:
        game.black.time_left -= dt

    white_clock.draw(DISPLAYSURF, game.white.time_left)
    black_clock.draw(DISPLAYSURF, game.black.time_left)

    boardImage.draw(DISPLAYSURF,highlighted_squares=(r,c))

    # Draw promotion 'animation' if there's a promotion happening
    if prom:
        try:
            boardImage.draw_prom_pieces(DISPLAYSURF,r2,c2)
        except:
            pass

    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
         
        # Get user's click coords 
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            x, y = event.pos
            col = (x - 180) // SQUARE_SIZE
            row = (y - 130) // SQUARE_SIZE

            # Checks if a non-square coord was clicked 
            if row < 0 or row > 7 or col < 0 or col > 7:
                continue
            
            # If a promotion is happening, checks if the user selected a piece to promote to 
            if prom and not prom_piece:
                prom_piece = coord_to_piece(c2,row,col,game.turn)
            
            elif None not in (r,c):
                r2 = row
                c2 = col
            else:
                r = row
                c = col

    if game.turn == PieceColor.BLACK:
        game.toggle_robot_move()
        boardImage.pieces = [PieceImage(piece,(SQUARE_SIZE,SQUARE_SIZE)) for piece in game.board.board.flat if piece]  

    # Applies selected move
    elif None not in (r, c, r2, c2):
        # Checks if the user is trying to perform a valid promotion.
        if not prom and game.can_toggle_promotion(r,c,r2,c2):
            prom = True
        # This next if clause will trigger in two cases:
        # -> The user is trying to perform a non-promotion move.
        # -> The user is trying to perfrom a promotion and already selected a piece to promote to. 
        elif not prom or prom_piece:
            try:
                move = game.play_move(r,c,r2,c2,prom_piece)
                # boardImage.apply_move(move)
                boardImage.pieces = [PieceImage(piece,(SQUARE_SIZE,SQUARE_SIZE)) for piece in game.board.board.flat if piece]            
            except GameNotInProgress:
                pass
            except InvalidMove:
                pass
            if prom:
                prom = False
                prom_piece = None
            r = c = r2 = c2 = None

    pygame.display.update()
    FramePerSec.tick(FPS)
