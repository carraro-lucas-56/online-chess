import pygame
from pygame.locals import *

from .colors import RED, WHITE

class GameMenu:
    def __init__(self, rect_size: tuple[int,int], screen_center: tuple[int,int]):
        (w,l) = rect_size
        (x,y) = screen_center

        dist_between_msgs = 20

        self.play_online_msg_rect =  Rect((x-w/2,y+l/2+dist_between_msgs/2),rect_size)
        self.play_bot_msg_rect =  Rect((x-w/2,y-l/2-dist_between_msgs/2),rect_size)
        
        font = pygame.font.Font(None,60)

        self.play_online_msg = font.render("Play online", True, WHITE)
        self.play_bot_msg = font.render("Play bot", True, WHITE)
        
    def draw(self, surface: pygame.Surface):
        pygame.draw.rect(surface,
                         RED,
                         self.play_online_msg_rect)
        
        pygame.draw.rect(surface,
                         RED,
                         self.play_bot_msg_rect)

        surface.blit(self.play_online_msg, self.play_online_msg_rect)
        surface.blit(self.play_bot_msg, self.play_bot_msg_rect)
        