import sys
import threading
import copy
import queue
import logging

import  pygame
from pygame.locals import *

from assets import load_assets
from chess.chessgame import ChessGame, GameState, InvalidMove, GameNotInProgress
from chess.piece import PieceColor, PieceType, Move
from render.board_view import BoardImage, PieceImage, to_board_coords
from render.colors import BLACK, GREY
from render.hud import Hud
from render.menu import GameMenu
from chess.AI import Engine
from utils.utils import is_light_square, in_bound
from network import Network

logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

# =======================================================
# ------------------ USEFUL FUNCTIONS -------------------
# =======================================================

def can_toggle_promotion(game: ChessGame, x: int, y: int, x2: int, y2: int) -> bool:
        """
        Recives the origin coord from a move and checks if the move can toggle.

        a promotion, i.e the coord has a pawn that's one rank away from promoting. 
        """
        if x < 0 or x > 7 or y < 0 or y > 7:
            return False
        
        elif not next((move for move in game.validMoves if move.coords == (x,y,x2,y2)), None):
            return False

        row = 1 if game.turn == PieceColor.WHITE else 6

        return (x == row 
                and game.board.board[x][y] 
                and game.board.board[x][y].color == game.turn 
                and game.board.board[x][y].type == PieceType.PAWN) 
    
def coord_to_piece(col: int, x: int, y: int, turn: PieceColor) -> PieceType | None:
    """
    Return the piece type that the user wants to promote to.

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

def get_opp_move(q: queue, 
                 waiting: threading.Event, 
                 stop_event: threading.Event,
                 n: Network,
                 lastMove: Move | None) -> None:
    """
    Sends the last move made and gets the opponent's next move.
    """
    
    waiting.set()
    
    try:
        if stop_event.is_set():
            return
        
        opp_move = n.send(lastMove)
        q.put(opp_move)

        if stop_event.is_set():
            return
        
    finally:
        waiting.clear()

# =======================================================
# --------------- GAME LOOP FUNCTIONS -------------------
# =======================================================

def play_bot_loop() -> None:
    game = ChessGame()
    game.start_game()

    user_color = PieceColor.WHITE

    # Initializing render objects
    hud = Hud(game,user_color,SQUARE_SIZE)
    boardImage = BoardImage(game,user_color,(SQUARE_SIZE,SQUARE_SIZE))

    # Variables to save user's click
    r = c = r2 = c2 = None

    # Variable to detect if a promotion is happening
    prom_happening = False 

    # Variable to save which piece the user wants to promote to
    prom_piece = None 

    stop_event = threading.Event()

    engine = Engine()

    quit = False

    while not quit:
        DISPLAYSURF.fill(GREY)

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.KEYDOWN and event.key == pygame.K_q:
                quit = True
                stop_event.set()

            # Get user's click coords (if it's the user's turn)
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                x, y = event.pos
                col = (x - 180) // SQUARE_SIZE
                row = (y - 130) // SQUARE_SIZE

                # Checks if a non-square coord was clicked 
                if row < 0 or row > 7 or col < 0 or col > 7:
                    continue
                
                # If a promotion is happening, checks if the user selected a piece to promote to 
                if prom_happening and not prom_piece:
                    prom_piece = coord_to_piece(c2,row,col,game.turn)

                elif None not in (r,c):
                    r2 = row
                    c2 = col
                else:
                    r = row
                    c = col

        # Applies selected move
        if None not in (r, c, r2, c2) and not quit:
            # Engine's turn
            if engine.thinking.is_set():
                r = c = r2 = c2 = None

            # Checks if the user is trying to perform a valid promotion.
            elif not prom_happening and can_toggle_promotion(game,r,c,r2,c2):
                prom_happening = True

            # This next if clause will trigger in two cases:
            # -> The user is trying to perform a non-promotion move.
            # -> The user is trying to perfrom a promotion and already selected a piece to promote to. 
            elif not prom_happening or prom_piece:
                try:
                    game.play_move_coords(r,c,r2,c2,prom_piece)
                    boardImage.pieces = [PieceImage.from_piece_obj(piece,user_color,(SQUARE_SIZE,SQUARE_SIZE)) for piece in game.board.board.flat if piece]            
                    # Start thread to get the engine's move
                    if game.state == GameState.IN_PROGRESS and (engine.thread is None or not engine.thread.is_alive()):
                        snapshot = copy.deepcopy(game)
                        engine.start_engine_thread(snapshot,stop_event)
                except (GameNotInProgress, InvalidMove):
                    pass

                if prom_happening:
                    prom_happening = False
                    prom_piece = None
                r = c = r2 = c2 = None

        # Applies engine move
        if not engine.move_queue.empty():
            try:
                engine_move = engine.move_queue.get_nowait()
                game.play_move(engine_move)
                boardImage.pieces = [PieceImage.from_piece_obj(piece,user_color,(SQUARE_SIZE,SQUARE_SIZE)) for piece in game.board.board.flat if piece]            
                r = c = r2 = c2 = None
            except (GameNotInProgress, InvalidMove):
                pass

        boardImage.draw(DISPLAYSURF,game.snapshots[-1].lastMove,selected_square=(r,c))
        hud.draw(DISPLAYSURF)

        if prom_happening:
            boardImage.draw_prom_pieces(DISPLAYSURF,r2,c2)

        pygame.display.update()
        FramePerSec.tick(FPS)

def play_online_loop() -> None:
    clock = pygame.time.Clock()

    n = Network()

    user_color = n.connect()

    game = ChessGame()
    game.start_game()

    # Initializing render objects
    hud = Hud(game,user_color,SQUARE_SIZE)
    boardImage = BoardImage(game,user_color,(SQUARE_SIZE,SQUARE_SIZE))

    # Variables to save user's click
    r = c = r2 = c2 = None

    # Variable to detect if a promotion is happening
    prom_happening = False 

    # Variable to save which piece the user wants to promote to
    prom_piece = None 

    # Threading variables
    waiting = threading.Event()
    stop_event = threading.Event()
    opp_thread = None

    # Queue for storing opponent's move
    q = queue.Queue()

    quit = False

    if user_color == PieceColor.BLACK:
        opp_thread = threading.Thread(target=get_opp_move,
                                      args=[q,waiting,stop_event,n,None],
                                      daemon=True)
        opp_thread.start()

    while not quit:
        DISPLAYSURF.fill(GREY)

        dt = clock.tick(FPS) / 1000  # seconds

        if game.turn == PieceColor.WHITE:
            game.white.time_left -= dt
        else:
            game.black.time_left -= dt

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.KEYDOWN and event.key == pygame.K_q:
                stop_event.set()
                quit = True

            # Get user's click coords (if it's the user's turn)
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                x, y = event.pos
                col = (x - 180) // SQUARE_SIZE
                row = (y - 130) // SQUARE_SIZE

                row, col = to_board_coords(row,col,user_color)

                # Checks if a non-square coord was clicked 
                if not in_bound(row,col):
                    continue
                
                # If a promotion is happening, checks if the user selected a piece to promote to 
                if prom_happening and not prom_piece:
                    prom_piece = coord_to_piece(c2,row,col,game.turn)

                elif None not in (r,c):
                    r2,c2 = row, col
                else:
                    r,c = row, col

        # Applies selected move
        if None not in (r, c, r2, c2) and not quit and not waiting.is_set() and game.state == GameState.IN_PROGRESS:
            # Checks if the user is trying to perform a valid promotion.
            if not prom_happening and can_toggle_promotion(game,r,c,r2,c2):
                prom_happening = True

            # This next if clause will trigger in two cases:
            # -> The user is trying to perform a non-promotion move.
            # -> The user is trying to perfrom a promotion and already selected a piece to promote to. 
            elif not prom_happening or prom_piece:
                try:
                    move = game.play_move_coords(r,c,r2,c2,prom_piece)
                    
                    # Starts thread to get the opponet's move
                    if (opp_thread is None or not opp_thread.is_alive()):
                        opp_thread = threading.Thread(target=get_opp_move,
                                                     args=[q,waiting,stop_event,n,move],
                                                     daemon=True)
                        opp_thread.start()
                    boardImage.pieces = [PieceImage.from_piece_obj(piece,user_color,(SQUARE_SIZE,SQUARE_SIZE)) 
                                                for piece in game.board.board.flat if piece]            
                except (GameNotInProgress, InvalidMove):
                    pass

                if prom_happening:
                    prom_happening = False
                    prom_piece = None
                r = c = r2 = c2 = None

        # Applies the opponent's move
        if not q.empty():
            try:
                opp_move = q.get_nowait()
                game.play_move(opp_move)
                boardImage.pieces = [PieceImage.from_piece_obj(piece,user_color,(SQUARE_SIZE,SQUARE_SIZE)) for piece in game.board.board.flat if piece]            
                r = c = r2 = c2 = None
            except (GameNotInProgress, InvalidMove):
                pass

        boardImage.draw(DISPLAYSURF,game.snapshots[-1].lastMove,selected_square=(r,c))
        hud.draw(DISPLAYSURF)

        if prom_happening:
            boardImage.draw_prom_pieces(DISPLAYSURF,r2,c2)

        pygame.display.update()
        FramePerSec.tick(FPS)

# =======================================================
# --------------- INITIALIZING VARIABLES ----------------
# =======================================================

# Initializing pygame
pygame.init()
 
# Setting up FPS 
FPS = 40
FramePerSec = pygame.time.Clock()

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 900
SQUARE_SIZE = 80
SCREEN_CENTER = (SCREEN_WIDTH/2,SCREEN_HEIGHT/2)

#Create a white screen 
DISPLAYSURF = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
pygame.display.set_caption("chess game")

load_assets()
menu = GameMenu((230,40),SCREEN_CENTER)

running = True

# ======================================================
# ----------------- MAIN PROGRAM LOOP ------------------
# ======================================================

while running:
    DISPLAYSURF.fill(BLACK)
    menu.draw(DISPLAYSURF)
    pygame.display.update()

    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            (x,y) = event.pos

            if menu.play_online_msg_rect.collidepoint((x,y)):
                play_online_loop()
            if menu.play_bot_msg_rect.collidepoint((x,y)):
                play_bot_loop()
            